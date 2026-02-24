# cars/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from .models import Car, UsedCar, News, User
from .forms import SignupForm, CarForm, UsedCarForm, NewsForm

# ----------------------------
# Public Pages
# ----------------------------
def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def order(request):
    return render(request, "order.html")


# ----------------------------
# Cars
# ----------------------------
def car_list(request):
    cars = Car.objects.all()
    return render(request, "cars/car_list.html", {"cars": cars})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, "cars/car_detail.html", {"car": car})

def compare_car(request):
    cars = Car.objects.all()
    return render(request, "cars/compare.html", {"cars": cars})

def inventory(request):
    cars = Car.objects.all()
    return render(request, "cars/inventory.html", {"cars": cars})

def upcoming_cars(request):
    cars = Car.objects.filter(is_upcoming=True)
    return render(request, "cars/upcoming_cars.html", {"cars": cars})

def electric_cars(request):
    cars = Car.objects.filter(is_electric=True)
    return render(request, "cars/electric_cars.html", {"cars": cars})

def find_new(request):
    query = request.GET.get("q", "")
    cars = Car.objects.filter(name__icontains=query)
    return render(request, "cars/find_new.html", {"cars": cars, "query": query})

def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("car_list")
    else:
        form = CarForm()
    return render(request, "cars/add_car.html", {"form": form})

def update_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect("car_list")
    else:
        form = CarForm(instance=car)
    return render(request, "cars/update_car.html", {"form": form, "car": car})

def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == "POST":
        car.delete()
        return redirect("car_list")
    return render(request, "cars/delete_car.html", {"car": car})


# ----------------------------
# Used Cars
# ----------------------------
def used_car_list(request):
    used_cars = UsedCar.objects.all()
    return render(request, "cars/used_car_list.html", {"used_cars": used_cars})

def add_used_car(request):
    if request.method == "POST":
        form = UsedCarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("used_car_list")
    else:
        form = UsedCarForm()
    return render(request, "cars/add_used_car.html", {"form": form})


# ----------------------------
# News
# ----------------------------
def news_list(request):
    news = News.objects.all()
    return render(request, "cars/news_list.html", {"news": news})

def add_news(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("news_list")
    else:
        form = NewsForm()
    return render(request, "cars/add_news.html", {"form": form})


# ----------------------------
# Signup / Auth
# ----------------------------
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "cars/signup.html", {"form": form})