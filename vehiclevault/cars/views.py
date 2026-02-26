from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import (
    CarListingForm,
    CarForm,
    CarListingImageForm,
    TestDriveForm,
)
from .models import (
    Car,
    CarCategory,
    Brand,
    DiscoveryPill,
    CarListing,
    TestDrive,
    CarListingImage,
)

User = get_user_model()

def seller_or_admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in [User.Role.SELLER, User.Role.ADMIN]:
            messages.error(request, "Seller or Admin access only 🚫")
            return redirect("cars:home")
        return view_func(request, *args, **kwargs)
    return wrapper

def HomeView(request):
    listings = (
        CarListing.objects
        .select_related("car", "seller")
        .prefetch_related("images")
        .order_by("-created_at")[:8]
    )
    return render(request, "home.html", {"listings": listings})

def find_new(request):
    return render(request, "cars/find_new.html")




def CarsListView(request):
    cars = Car.objects.order_by("-created_at")

    fuel = request.GET.get("fuel")
    budget = request.GET.get("budget")
    q = request.GET.get("q")
    brand = request.GET.get("brand")
    body_type = request.GET.get("body_type") or request.GET.get("filter")
    transmission = request.GET.get("transmission")
    seating = request.GET.get("seating")

    if fuel:
        cars = cars.filter(fuel_type__iexact=fuel)
    if q:
        cars = cars.filter(Q(brand__icontains=q) | Q(model__icontains=q))
    if brand:
        cars = cars.filter(brand__icontains=brand)
    if body_type:
        cars = cars.filter(category__name__icontains=body_type)
    if transmission:
        cars = cars.filter(transmission__iexact=transmission)
    if seating:
        cars = cars.filter(seating_capacity=seating)
    if budget:
        try:
            budget_lower = budget.lower()
            if "under" in budget_lower:
                # Expecting format "under-10-lakh" or "under-10"
                parts = [p for p in budget_lower.split("-") if p.isdigit()]
                if parts:
                    max_val = int(parts[0]) * 100000
                    cars = cars.filter(price__lt=max_val)
            elif "over" in budget_lower:
                # Expecting format "over-50-lakh" or "over-50"
                parts = [p for p in budget_lower.split("-") if p.isdigit()]
                if parts:
                    min_val = int(parts[0]) * 100000
                    cars = cars.filter(price__gt=min_val)
            elif "-" in budget:
                # Expecting format "5-10-lakh" or "5-10"
                parts = [p for p in budget.split("-") if p.isdigit()]
                if len(parts) >= 2:
                    min_val = int(parts[0]) * 100000
                    max_val = int(parts[1]) * 100000
                    cars = cars.filter(price__range=(min_val, max_val))
        except (ValueError, IndexError):
            pass # Invalid budget format, skip filtering

    pills = DiscoveryPill.objects.all()
    
    # Categorize pills for the multi-tab discovery section
    discovery_context = {
        "budget_pills": pills.filter(pill_type="Budget"),
        "body_pills": pills.filter(pill_type="Body Type"),
        "fuel_pills": pills.filter(pill_type="Fuel Type"),
        "transmission_pills": pills.filter(pill_type="Transmission"),
        "seating_pills": pills.filter(pill_type="Seating"),
        "popular_pills": pills.filter(pill_type="Popular"),
    }

    context = {
        "cars": cars.distinct(),
        "brands": Brand.objects.all(),
        **discovery_context,
    }

    return render(request, "cars/all_cars.html", context)

def UsedCarsListView(request):
    # Filtering for cars that have a listing and are NOT new (inventory/stock based logic)
    # Since we don't have a 'condition' field, we'll show all available car listings
    # as 'Used' implies pre-owned/listed by sellers.
    cars = Car.objects.filter(stock__gt=0).order_by("-created_at")
    return render(request, "cars/used_cars.html", {"cars": cars})

@seller_or_admin_required
def InventoryListView(request):
    if request.user.role == User.Role.ADMIN:
        cars = Car.objects.all().order_by("-created_at")
    else:
        cars = Car.objects.filter(seller=request.user).order_by("-created_at")
    
    return render(request, "cars/inventory.html", {"cars": cars})

def UpcomingCarsListView(request):
    # Filtering for cars with future launch year (2026+)
    cars = Car.objects.filter(launch_year__gte=2026).order_by("launch_year")
    return render(request, "cars/upcoming_cars.html", {"cars": cars})

def ElectricCarsListView(request):
    # Filtering for cars with fuel_type='Electric'
    # Checking for common variations just in case
    cars = Car.objects.filter(
        Q(fuel_type__iexact='Electric') | 
        Q(fuel_type__iexact='EV')
    ).order_by("-created_at")
    return render(request, "cars/electric_cars.html", {"cars": cars})

def NewCarsListView(request):
    # Filtering for current year models (2025)
    cars = Car.objects.filter(launch_year=2025).order_by("-created_at")
    return render(request, "cars/new_cars.html", {"cars": cars})

def CarDetailView(request, vin):
    car = get_object_or_404(Car, vin=vin)
    return render(request, "cars/car_detail.html", {"car": car})

def CarCategoryView(request, category_name):
    category = get_object_or_404(CarCategory, name__iexact=category_name)
    cars = Car.objects.filter(category=category).order_by("-created_at").select_related("seller")
    
    context = {
        "category": category,
        "cars": cars,
        "category_name": category_name
    }
    return render(request, "cars/car_category.html", context)

@seller_or_admin_required
def CarCreateView(request):
    form = CarForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        car = form.save(commit=False)
        car.seller = request.user
        
        # Handle the manual file input from template
        images = request.FILES.getlist("images")
        if images and not car.car_image:
            car.car_image = images[0]
            
        car.save()

        messages.success(request, "Car added successfully 🚗")
        return redirect("cars:inventory")

    return render(request, "cars/add_car.html", {
        "car_form": form,
    })
@seller_or_admin_required
def CarUpdateView(request, vin):
    if request.user.role == User.Role.ADMIN:
        car = get_object_or_404(Car, vin=vin)
    else:
        car = get_object_or_404(Car, vin=vin, seller=request.user)

    form = CarForm(request.POST or None, request.FILES or None, instance=car)

    if request.method == "POST" and form.is_valid():
        car = form.save(commit=False)
        
        images = request.FILES.getlist("images")
        if images and not car.car_image:
            car.car_image = images[0]
            
        car.save()

        messages.success(request, "Car updated successfully ✨")
        return redirect("cars:inventory")

    return render(request, "cars/add_car.html", {
        "car_form": form,
        "car": car
    })

@seller_or_admin_required
def CarDeleteView(request, vin):
    if request.user.role == User.Role.ADMIN:
        car = get_object_or_404(Car, vin=vin)
    else:
        car = get_object_or_404(Car, vin=vin, seller=request.user)
    car.delete()
    messages.success(request, "Car deleted successfully 🗑️")
    return redirect("cars:all_cars")

def compare_cars(request):
    compare_list = request.session.get("compare_list", [])
    cars = Car.objects.filter(id__in=compare_list)
    return render(request, "cars/compare.html", {"cars": cars})


def add_to_compare(request, car_id):
    compare_list = request.session.get("compare_list", [])

    if car_id not in compare_list:
        compare_list = (compare_list + [car_id])[-2:]
        request.session["compare_list"] = compare_list
        messages.success(request, "Car added to compare 🔍")
    else:
        messages.info(request, "Already in compare list")

    return redirect("cars:compare_cars")

def remove_from_compare(request, car_id):
    compare_list = request.session.get("compare_list", [])
    if car_id in compare_list:
        compare_list.remove(car_id)
        request.session["compare_list"] = compare_list
        messages.success(request, "Removed from compare ❌")
    return redirect("cars:compare_cars")

@login_required
def TestDrivesView(request):
    if request.user.role == User.Role.BUYER:
        base_qs = (
            TestDrive.objects.filter(buyer=request.user)
            .select_related("listing__car", "listing__seller")
            .prefetch_related("listing__images")
        )
    else:
        base_qs = (
            TestDrive.objects.filter(listing__seller=request.user)
            .select_related("listing__car", "buyer")
            .prefetch_related("listing__images")
        )

    drives = base_qs.order_by("-created_at")
    
    # Calculate stats for the dashboard header
    stats = {
        'total': drives.count(),
        'pending': base_qs.filter(status='Pending').count(),
        'confirmed': base_qs.filter(status='Confirmed').count(),
    }

    return render(request, "testdrives/list.html", {
        "drives": drives,
        "stats": stats
    })

@login_required
def UpdateTestDriveStatusView(request, drive_id, status):
    drive = get_object_or_404(TestDrive, test_drive_id=drive_id)
    
    # Permission check: Only the seller of the listing can update status
    if drive.listing.seller != request.user and request.user.role != User.Role.ADMIN:
        messages.error(request, "Unauthorized access 🚫")
        return redirect("cars:test_drives")
        
    valid_statuses = dict(TestDrive._meta.get_field('status').choices).keys()
    if status in valid_statuses:
        drive.status = status
        drive.save()
        messages.success(request, f"Test drive status updated to {status} ✅")
    else:
        messages.error(request, "Invalid status update 😬")
        
    return redirect("cars:test_drives")