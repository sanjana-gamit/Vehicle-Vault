from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from cars.forms import (
    CarListingForm,
    CarForm,
    CarListingImageForm,
    TestDriveForm,
    BuyerTestDriveForm,
    PurchaseForm,
)
from cars.models import (
    Car,
    CarCategory,
    Brand,
    DiscoveryPill,
    CarListing,
    TestDrive,
    CarImage,
    Purchase,
    Message,
    Deal,
    ActivityLog,
    UserTask,
    Wishlist,
)
from cars.utils import log_activity
import razorpay
import uuid


User = get_user_model()

def seller_or_admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in [User.Role.SELLER, User.Role.ADMIN]: # type: ignore
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
    brands = Brand.objects.all().order_by('order', 'name')
    return render(request, "home.html", {
        "listings": listings,
        "brands": brands
    })

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
                parts = [p for p in budget_lower.split("-") if p.isdigit()]
                if parts:
                    max_val = int(parts[0]) * 100000
                    cars = cars.filter(price__lt=max_val)
            elif "over" in budget_lower:
                parts = [p for p in budget_lower.split("-") if p.isdigit()]
                if parts:
                    min_val = int(parts[0]) * 100000
                    cars = cars.filter(price__gt=min_val)
            elif "-" in budget:
                parts = [p for p in budget.split("-") if p.isdigit()]
                if len(parts) >= 2:
                    min_val = int(parts[0]) * 100000
                    max_val = int(parts[1]) * 100000
                    cars = cars.filter(price__range=(min_val, max_val))
        except (ValueError, IndexError):
            pass 

    pills = DiscoveryPill.objects.all()
    
    discovery_context = {
        "budget_pills": pills.filter(pill_type="Budget"),
        "body_pills": pills.filter(pill_type="Body Type"),
        "fuel_pills": pills.filter(pill_type="Fuel Type"),
        "transmission_pills": pills.filter(pill_type="Transmission"),
        "seating_pills": pills.filter(pill_type="Seating"),
        "popular_pills": pills.filter(pill_type="Popular"),
    }

    static_car_images = [
        {"name": "Audi", "file": "Audi.jpg"},
        {"name": "BMW", "file": "BMW.jpg"},
        {"name": "Kia", "file": "Kia.jpg"},
        {"name": "MG", "file": "MG.jpg"},
        {"name": "Mahindra", "file": "Mahindra.jpg"},
        {"name": "Mercedes", "file": "Mercedes.jpg"},
        {"name": "Nissan", "file": "Nissan.jpg"},
        {"name": "Swift", "file": "Swift.jpg"},
        {"name": "Tata", "file": "Tata.jpg"},
        {"name": "Honda", "file": "honda.jpg"},
        {"name": "Hyundai", "file": "download.jpg"},
    ]

    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = Wishlist.objects.filter(user=request.user).values_list("car_id", flat=True)

    context = {
        "cars": cars.distinct(),
        "brands": Brand.objects.all(),
        "static_car_images": static_car_images,
        "wishlisted_ids": list(wishlisted_ids),
        **discovery_context,
    }

    return render(request, "cars/all_cars.html", context)

def UsedCarsListView(request):
    cars = Car.objects.filter(stock__gt=0).order_by("-created_at")
    return render(request, "cars/used_cars.html", {"cars": cars})

@seller_or_admin_required
def InventoryListView(request):
    if request.user.role == User.Role.ADMIN: # type: ignore
        cars = Car.objects.all().order_by("-created_at")
    else:
        cars = Car.objects.filter(seller=request.user).order_by("-created_at")
    
    return render(request, "cars/inventory.html", {"cars": cars})

def UpcomingCarsListView(request):
    cars = Car.objects.filter(launch_year__gte=2026).order_by("launch_year")
    return render(request, "cars/upcoming_cars.html", {"cars": cars})

def ElectricCarsListView(request):
    cars = Car.objects.filter(
        Q(fuel_type__iexact="Electric") | 
        Q(fuel_type__iexact="EV")
    ).order_by("-created_at")
    return render(request, "cars/electric_cars.html", {"cars": cars})

def NewCarsListView(request):
    cars = Car.objects.filter(launch_year=2025).order_by("-created_at")
    return render(request, "cars/new_cars.html", {"cars": cars})

def CarDetailView(request, vin):
    car = get_object_or_404(Car, vin=vin)
    
    brand = Brand.objects.filter(name__iexact=car.brand).first()
    similar_cars = Car.objects.filter(
        Q(category=car.category) | Q(brand=car.brand)
    ).exclude(vin=car.vin)[:4]
    
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, car=car).exists()

    context = {
        "car": car,
        "brand": brand,
        "similar_cars": similar_cars,
        "is_wishlisted": is_wishlisted
    }
    return render(request, "cars/car_detail.html", context)

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
        
        images = request.FILES.getlist("images")
        if images and not car.car_image:
            car.car_image = images[0]
            
        car.save()
        
        # Populate the Multi-Image Media Gallery
        if images:
            for img in images:
                CarImage.objects.create(car=car, image=img)

        log_activity(request.user, "Listing Created", f"New asset '{car.brand} {car.model}' (VIN: {car.vin}) registered in inventory.")
        messages.success(request, "Asset registered successfully with multi-media gallery 📸")
        return redirect("cars:inventory")

    return render(request, "cars/add_car.html", {
        "car_form": form,
    })

@seller_or_admin_required
def CarUpdateView(request, vin):
    if request.user.role == User.Role.ADMIN: # type: ignore
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
        
        # Append additional media to the existing gallery
        if images:
            for img in images:
                CarImage.objects.create(car=car, image=img)

        log_activity(request.user, "Listing Updated", f"Asset '{car.brand} {car.model}' (VIN: {car.vin}) specifications revised.")
        messages.success(request, "Asset updated successfully ✨")
        return redirect("cars:inventory")

    return render(request, "cars/add_car.html", {
        "car_form": form,
        "car": car
    })

@seller_or_admin_required
def CarDeleteView(request, vin):
    if request.user.role == User.Role.ADMIN: # type: ignore
        car = get_object_or_404(Car, vin=vin)
    else:
        car = get_object_or_404(Car, vin=vin, seller=request.user)
    log_activity(request.user, "Listing Deleted", f"Asset '{car.brand} {car.model}' (VIN: {car.vin}) permanently removed.")
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
        compare_list = (compare_list + [car_id])[-4:]
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
def ScheduleTestDriveView(request, vin):
    car = get_object_or_404(Car, vin=vin)
    listing = car.listings.first() # type: ignore
    
    if not listing:
        messages.error(request, "No active listing found for this vehicle. 🚫")
        return redirect("cars:car_detail", vin=vin)

    if request.user.role != User.Role.BUYER: # type: ignore
        messages.error(request, "Only registered buyers can request test drives. 🏎️")
        return redirect("cars:car_detail", vin=vin)

    form = BuyerTestDriveForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        test_drive = form.save(commit=False)
        test_drive.listing = listing
        test_drive.buyer = request.user
        test_drive.status = "Pending"
        test_drive.save()

        # Task and Activity integration
        UserTask.objects.create(
            user=listing.seller,
            title=f"New Test Drive Request: {car.brand} {car.model}",
            description=f"Buyer {request.user.name} requested a test drive on {test_drive.proposed_date}.",
        )
        log_activity(request.user, "Test Drive Requested", f"Requested test drive for {car.brand} {car.model} on {test_drive.proposed_date}")
        
        messages.success(request, "Test drive requested successfully! The seller will confirm shortly. ✨")
        return redirect("cars:test_drives")

    return render(request, "testdrives/new.html", {
        "form": form,
        "car": car,
        "listing": listing
    })

@login_required
def TestDrivesView(request):
    if request.user.role == User.Role.BUYER: # type: ignore
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
    
    stats = {
        "total": drives.count(),
        "pending": base_qs.filter(status="Pending").count(),
        "confirmed": base_qs.filter(status="Confirmed").count(),
    }

    return render(request, "testdrives/list.html", {
        "drives": drives,
        "stats": stats
    })

@login_required
def UpdateTestDriveStatusView(request, drive_id, status):
    drive = get_object_or_404(TestDrive, test_drive_id=drive_id)
    
    if drive.listing.seller != request.user and request.user.role != User.Role.ADMIN: # type: ignore
        messages.error(request, "Unauthorized access 🚫")
        return redirect("cars:test_drives")

    valid_statuses = dict(TestDrive._meta.get_field("status").choices).keys() # type: ignore
    if status in valid_statuses:
        drive.status = status
        drive.save()
        log_activity(request.user, "Test Drive Updated", f"Status of test drive for {drive.listing.car} changed to '{status}'.")
        messages.success(request, f"Test drive status updated to {status} ✅")
    else:
        messages.error(request, "Invalid status update 😬")
        
    return redirect("cars:test_drives")

@login_required
def PurchaseCarView(request, vin):
    car = get_object_or_404(Car, vin=vin)
    deal_id_str = request.GET.get('deal_id')
    
    # Validate deal_id is a valid UUID
    deal_id = None
    if deal_id_str:
        try:
            deal_id = uuid.UUID(deal_id_str)
        except (ValueError, TypeError):
            deal_id = None
    
    if request.user.role != User.Role.BUYER: # type: ignore

        messages.error(request, "Only buyers can purchase cars 🛒")
        return redirect("cars:car_detail", vin=vin)
    
    # Honor negotiated deal price if active
    final_price = car.price
    if deal_id:
        active_deal = Deal.objects.filter(deal_id=deal_id, buyer=request.user, status='Accepted').first()

        if active_deal:
            final_price = active_deal.offered_price
            
    form = PurchaseForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        purchase = form.save(commit=False)
        purchase.user = request.user
        purchase.car = car
        purchase.price = final_price
        
        charge_amount = float(final_price)
        
        if purchase.payment_method == "EMI":
            purchase.is_emi = True
            months = int(form.cleaned_data["emi_months"])
            down_payment = float(form.cleaned_data["down_payment"])
            principal = float(final_price) - down_payment
            # Proper compound interest EMI formula: EMI = P * r(1+r)^n / ((1+r)^n - 1)
            annual_rate = 0.10  # 10% p.a.
            r = annual_rate / 12  # monthly rate
            n = months
            if r > 0:
                emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            else:
                emi = principal / n
            purchase.monthly_installment = float(f"{emi:.2f}")
            purchase.emi_months = months
            purchase.down_payment = down_payment
            charge_amount = down_payment
            
        if purchase.is_token_booking:
            charge_amount = 50000.00
            
        # Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(charge_amount * 100)
        
        # Generate official Razorpay Order
        razorpay_order = client.order.create({ # type: ignore
            "amount": amount_in_paise,
            "currency": 'INR',
            "payment_capture": '1' 
        })
        
        purchase.razorpay_order_id = razorpay_order['id']
        purchase.payment_status = "Pending" 
        purchase.save()
        
        return render(request, "cars/razorpay_checkout.html", {
            "purchase": purchase,
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
            "amount": charge_amount,
            "amount_in_paise": amount_in_paise,
            "car": car
        })

    return render(request, "cars/purchase_checkout.html", {
        "car": car,
        "form": form
    })

@login_required
def RazorpayCallbackView(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        purchase_id = request.POST.get('purchase_id', '')
        
        if not all([payment_id, order_id, signature, purchase_id]):
            messages.error(request, "Invalid gateway payload 🚫")
            return redirect("core:buyer_dashboard")
            
        purchase = get_object_or_404(Purchase, purchase_id=purchase_id)
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({ # type: ignore
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            
            # Signature Verified Successfully
            purchase.razorpay_payment_id = payment_id
            purchase.razorpay_signature = signature
            purchase.payment_status = "Completed"
            purchase.save()
            
            # Inventory Automation
            car = purchase.car
            if car.stock > 0:
                car.stock -= 1
                car.save()
                
            # Mark listing as Sold (unless it's just a token booking and not full acquisition)
            listing = car.listings.first() # type: ignore
            if listing and not purchase.is_token_booking:
                listing.status = "Sold"
                listing.save()
                
            # Executive Invoicing Automation
            amount_secured = 50000.00 if purchase.is_token_booking else purchase.price
                
            ctx = {
                'user_name': purchase.user.name or purchase.user.email,
                'car_brand': car.brand,
                'car_model': car.model,
                'car_vin': car.vin,
                'purchase': purchase,
                'amount': amount_secured
            }
            
            html_content = render_to_string('cars/emails/invoice.html', ctx)
            
            # Dispatch to Buyer
            msg_buyer = EmailMultiAlternatives(
                subject=f"Vault Authorization Verified: {car.brand} {car.model}",
                body="Your transaction has been securely captured.",
                from_email=settings.EMAIL_HOST_USER,
                to=[purchase.user.email]
            )
            msg_buyer.attach_alternative(html_content, "text/html")
            msg_buyer.send(fail_silently=True)
            
            # Dispatch to Seller / Logistics
            seller_email = listing.seller.email if listing else "admin@vehiclevault.com"
            msg_seller = EmailMultiAlternatives(
                subject=f"Asset Secured Alert: {car.brand} {car.model} Acquired",
                body="A client has successfully captured this asset via the Vault Payment Protocol.",
                from_email=settings.EMAIL_HOST_USER,
                to=[seller_email]
            )
            msg_seller.attach_alternative(html_content, "text/html")
            msg_seller.send(fail_silently=True)
                
            messages.success(request, f"Cryptographic Verification Complete! ✨ You've officially secured the {car.brand} {car.model}.")
            # Log payment success for both buyer and seller
            log_activity(purchase.user, "Payment Completed", f"Full payment secured for {car.brand} {car.model} (₹{purchase.price}).")
            if listing and listing.seller:
                log_activity(listing.seller, "Asset Sold", f"{car.brand} {car.model} acquired by {purchase.user.name or purchase.user.email} for ₹{purchase.price}.")
            return redirect("cars:purchase_success", purchase_id=purchase.purchase_id)
            
        except razorpay.errors.SignatureVerificationError: # type: ignore
            messages.error(request, "Gateway Security Warning: Invalid signature. Transaction Reversed ⚠️")
            purchase.payment_status = "Cancelled"
            purchase.save()
            return redirect("cars:car_detail", vin=purchase.car.vin)

    return redirect("core:buyer_dashboard")

@login_required
def PurchaseSuccessView(request, purchase_id):
    purchase = get_object_or_404(Purchase, purchase_id=purchase_id)
    return render(request, "cars/purchase_success.html", {"purchase": purchase})

@login_required
def InboxView(request):
    # Get all unique users the current user has messaged or received messages from
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True)
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True)
    
    user_ids = set(list(sent_to) + list(received_from))
    contacts = User.objects.filter(user_id__in=user_ids)
    
    return render(request, "messaging/inbox.html", {"contacts": contacts})

@login_required
def ChatView(request, other_user_id):
    other_user = get_object_or_404(User, user_id=other_user_id)
    listing_id = request.GET.get('listing_id')
    listing = None
    if listing_id:
        listing = get_object_or_404(CarListing, listing_id=listing_id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                listing=listing,
                content=content
            )
            log_activity(request.user, "Message Sent", f"Sent message to {other_user.email}")
            return redirect('cars:chat', other_user_id=other_user_id)

    messages_list = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('created_at')
    
    # Mark received messages as read
    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    # Active deal bridging
    active_deal = None
    buyer = request.user if request.user.role == 'Buyer' else other_user
    seller = request.user if request.user.role == 'Seller' else other_user
    
    if buyer.role == 'Buyer' and seller.role == 'Seller': # type: ignore
        deal_qs = Deal.objects.filter(buyer=buyer, listing__seller=seller).exclude(status__in=['Rejected', 'Cancelled']).order_by('-updated_at')
        if listing:
            deal_qs = deal_qs.filter(listing=listing)
        active_deal = deal_qs.first()
    
    return render(request, "messaging/chat.html", {
        "other_user": other_user,
        "chat_messages": messages_list,
        "listing": listing,
        "active_deal": active_deal
    })

@login_required
def ProposeDealView(request, listing_id):
    listing = get_object_or_404(CarListing, listing_id=listing_id)
    
    if request.method == "POST":
        offered_price = request.POST.get('offered_price')
        message = request.POST.get('message', '')
        
        deal = Deal.objects.create(
            listing=listing,
            buyer=request.user,
            offered_price=offered_price,
            message=message
        )
        
        # Create a task for the seller
        UserTask.objects.create(
            user=listing.seller,
            title=f"New Offer: {listing.car}",
            description=f"Buyer {request.user.name} offered ₹{offered_price}. Message: {message}",
        )
        
        log_activity(request.user, "Deal Proposed", f"Proposed ₹{offered_price} for {listing.car}")
        messages.success(request, "Proposal transmitted successfully! 🚀")
        return redirect('cars:car_detail', vin=listing.car.vin)

    return render(request, "deals/propose.html", {"listing": listing})

@login_required
def UpdateDealStatusView(request, deal_id, status):
    deal = get_object_or_404(Deal, deal_id=deal_id)
    
    # Authorized? (Seller of the listing or Buyer of the deal)
    if request.user != deal.listing.seller and request.user != deal.buyer:
        messages.error(request, "Unauthorized 🚫")
        return redirect('cars:all_cars')

    if status in Deal.Status.values:
        deal.status = status
        deal.save()
        
        # Log activity
        log_activity(request.user, "Deal Updated", f"Deal status changed to {status} for {deal.listing.car}")
        
        # If accepted, maybe update listing status?
        if status == Deal.Status.ACCEPTED:
            deal.listing.status = "Pending"
            deal.listing.save()
            messages.success(request, "Deal accepted! The listing is now PENDING. 🤝")
        else:
            messages.info(request, f"Deal marked as {status}.")
            
    return redirect('core:seller_dashboard' if request.user.role == 'Seller' else 'core:buyer_dashboard')

@seller_or_admin_required
def WithdrawListingView(request, listing_id):
    listing = get_object_or_404(CarListing, listing_id=listing_id)
    
    # Control
    if request.user != listing.seller and request.user.role != User.Role.ADMIN: # type: ignore
        messages.error(request, "Unauthorized 🚫")
        return redirect('cars:inventory')

    listing.status = "Withdrawn"
    listing.save()
    
    log_activity(request.user, "Listing Withdrawn", f"Withdrew {listing.car} from inventory.")
    messages.warning(request, "Listing has been successfully withdrawn. 🗑️")
    return redirect('cars:inventory')


@login_required
def toggle_wishlist(request, car_id):
    """Add or remove a car from the user's wishlist. Returns to the page they came from."""
    car = get_object_or_404(Car, id=car_id)
    existing = Wishlist.objects.filter(user=request.user, car=car).first()

    if existing:
        existing.delete()
        messages.info(request, f"{car.brand} {car.model} removed from your wishlist.")
    else:
        Wishlist.objects.create(user=request.user, car=car)
        log_activity(request.user, "Wishlist Updated", f"Saved {car.brand} {car.model} to wishlist.")
        messages.success(request, f"{car.brand} {car.model} saved to your wishlist ❤️")

    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "cars:all_cars"
    return redirect(next_url)


@login_required
def wishlist_page(request):
    """Show all cars saved in the buyer's wishlist."""
    items = Wishlist.objects.filter(user=request.user).select_related("car__category")
    return render(request, "cars/wishlist.html", {"wishlist_items": items})
