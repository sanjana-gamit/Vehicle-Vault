from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserLoginForm, UserSignupForm 
from cars.models import User, Buyer, Seller 
from django.shortcuts import get_object_or_404

def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.ADMIN:
            messages.error(request, "Access Denied: Admins Only 🚫")
            return redirect("cars:home")
        return view_func(request, *args, **kwargs)
    return wrapper

def UserLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)

            if user:
                selected_role = form.cleaned_data.get("role")
                if user.role != selected_role:
                    messages.error(request, f"Access Denied: You are not registered as a {selected_role} 🚫")
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.name or user.email}! 🔓")

                    # Redirect to role-based dashboard
                    if user.role == "Admin":
                        return redirect("core:admin_dashboard")
                    elif user.role in ["Seller", "Dealer"]:
                        return redirect("core:seller_dashboard")
                    else:
                        return redirect("core:buyer_dashboard")
            else:
                messages.error(request, "Invalid email or password 😬")
    else:
        form = UserLoginForm()

    return render(request, "core/login.html", {"form": form})


def UserSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            role = form.cleaned_data["role"]
            if role == User.Role.BUYER:
                Buyer.objects.create(user=user)
            elif role in [User.Role.SELLER, User.Role.DEALER]:
                Seller.objects.create(user=user)

            # Log the user in immediately after signup
            login(request, user)
            messages.success(request, "Account created successfully! 🎉")

            # Redirect to role-based dashboard
            if user.role == "Admin":
                return redirect("core:admin_dashboard")
            elif user.role == "Seller":
                return redirect("core:seller_dashboard")
            else:
                return redirect("core:buyer_dashboard")
    else:
        form = UserSignupForm()

    return render(request, "core/signup.html", {"form": form})


def LogoutViewCustom(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully 👋")
    else:
        messages.info(request, "You’re already logged out 🙂")

    return redirect("core:login")
    # ❌ DO NOT render logout.html here if you're redirecting


def contact(request):
    return render(request, "core/contact.html")


def faq(request):
    return render(request, "core/faq.html")


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")


def about(request):
    return render(request, "core/about.html")

def car_loan(request):
    return render(request, "core/car_loan.html")

def car_insurance(request):
    return render(request, "core/car_insurance.html")

def car_valuation(request):
    return render(request, "core/car_valuation.html")

def sell_car(request):
    return render(request, "core/sell_car.html")

def help_center(request):
    return render(request, "core/help_center.html")

def sitemap(request):
    return render(request, "core/sitemap.html")

def loan_application(request):
    return render(request, "core/loan_application.html")

def insurance_quote(request):
    return render(request, "core/insurance_quote.html")

def valuation_check(request):
    return render(request, "core/valuation_check.html")

# =========================
# DASHBOARDS
# =========================

@login_required
def admin_dashboard(request):
    if request.user.role != "Admin":
        messages.error(request, "Access Denied: Admins Only")
        return redirect("cars:home")
    return render(request, "core/admin_dashboard.html")

@login_required
def seller_dashboard(request):
    if request.user.role not in ["Seller", "Dealer"]:
        messages.error(request, "Access Denied: Sellers & Dealers Only")
        return redirect("cars:home")
    return render(request, "core/seller_dashboard.html")

@login_required
def buyer_dashboard(request):
    if request.user.role != "Buyer":
        messages.error(request, "Access Denied: Buyers Only")
        return redirect("cars:home")
    return render(request, "core/buyer_dashboard.html")

# =========================
# USER MANAGEMENT
# =========================

@admin_required
def UserManageListView(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "core/manage_users.html", {"users": users})

@admin_required
def UserDeleteView(request, user_id):
    user_to_delete = get_object_or_404(User, user_id=user_id)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account! 🛑")
    else:
        user_to_delete.delete()
        messages.success(request, f"Account {user_to_delete.email} has been removed. 🗑️")
    return redirect("core:manage_users")