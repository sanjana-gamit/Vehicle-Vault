from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import UserLoginForm, UserSignupForm

def UserLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if user.role == User.Role.ADMIN:
                    return redirect("admin_dashboard")
                elif user.role == User.Role.SELLER:
                    return redirect("seller_dashboard")
                elif user.role == User.Role.BUYER:
                    return redirect("buyer_dashboard")
                messages.success(request, "Logged in successfully 🔓")
                return redirect("home")
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

            # Create buyer/seller profile
            role = form.cleaned_data["role"]
            if role == User.Role.BUYER:
                Buyer.objects.create(user=user)
            elif role == User.Role.SELLER:
                Seller.objects.create(user=user)

            messages.success(request, "Account created successfully! 🎉")
            return redirect("login")
    else:
        form = UserSignupForm()

    return render(request, "core/signup.html", {"form": form})

def LogoutViewCustom(request):
    logout(request)
    messages.success(request, "Logged out successfully 👋")
    return redirect("home")

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