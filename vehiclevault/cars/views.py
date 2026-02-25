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
    CarListing,
    TestDrive,
    CarListingImage,
)

User = get_user_model()

def seller_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.SELLER:
            messages.error(request, "Seller access only 🚫")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper

def HomeView(request):
    listings = (
        CarListing.objects
        .select_related("car", "seller")
        .prefetch_related("images", "car__images")
        .order_by("-created_at")[:8]
    )
    return render(request, "home.html", {"listings": listings})

def find_new(request):
    return render(request, "cars/find_new.html")

def news_list(request):
    return render(request, "cars/news_list.html")

def order(request):
    return render(request, "cars/order.html")


def CarsListView(request):
    cars = Car.objects.prefetch_related("images").order_by("-created_at")

    fuel = request.GET.get("fuel")
    q = request.GET.get("q")
    brand = request.GET.get("brand")

    if fuel:
        cars = cars.filter(fuel_type__iexact=fuel)
    if q:
        cars = cars.filter(Q(brand__icontains=q) | Q(model__icontains=q))
    if brand:
        cars = cars.filter(brand__icontains=brand)

    return render(request, "cars/all_cars.html", {"cars": cars.distinct()})

def CarCategoryView(request):
    return render(request, "cars/car_category.html")

@seller_required
def CarCreateView(request):
    form = CarForm(request.POST or None, request.FILES or None)
    image_form = CarImageUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid() and image_form.is_valid():
        car = form.save(commit=False)
        car.seller = request.user
        car.save()

        for img in request.FILES.getlist("images"):
            CarImage.objects.create(car=car, image=img)

        messages.success(request, "Car added successfully 🚗")
        return redirect("cars")

    return render(request, "cars/add_car.html", {
        "car_form": form,
        "image_form": image_form
    })
@seller_required
def CarUpdateView(request, vin):
    car = get_object_or_404(Car, vin=vin, seller=request.user)

    form = CarForm(request.POST or None, request.FILES or None, instance=car)
    image_form = CarImageUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid() and image_form.is_valid():
        form.save()

        for img in request.FILES.getlist("images"):
            CarImage.objects.create(car=car, image=img)

        messages.success(request, "Car updated successfully ✨")
        return redirect("cars")

    return render(request, "cars/add_car.html", {
        "car_form": form,
        "image_form": image_form,
        "car": car
    })

@seller_required
def CarDeleteView(request, vin):
    car = get_object_or_404(Car, vin=vin, seller=request.user)
    car.delete()
    messages.success(request, "Car deleted successfully 🗑️")
    return redirect("cars")

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

    return redirect("cars")

def remove_from_compare(request, car_id):
    compare_list = request.session.get("compare_list", [])
    if car_id in compare_list:
        compare_list.remove(car_id)
        request.session["compare_list"] = compare_list
        messages.success(request, "Removed from compare ❌")
    return redirect("compare_cars")

@login_required
def TestDrivesView(request):
    if request.user.role == User.Role.BUYER:
        drives = TestDrive.objects.filter(buyer=request.user)
    else:
        drives = TestDrive.objects.filter(listing__seller=request.user)

    return render(request, "testdrives/list.html", {"drives": drives})