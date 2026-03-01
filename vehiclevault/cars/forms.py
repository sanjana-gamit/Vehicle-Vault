from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    User,
    Buyer,
    Seller,
    CarCategory,
    Car,
    CarListing,
    CarListingImage,
    TestDrive,
)

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "phone", "role", "password1", "password2")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

class CarCategoryForm(forms.ModelForm):
    class Meta:
        model = CarCategory
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"})
        }
    def clean_name(self):
        name = self.cleaned_data["name"].lower()
        if CarCategory.objects.filter(name=name).exists():
            raise ValidationError("Category already exists.")
        return name

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ("created_at", "is_available", "slug", "seller")
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "vin": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "fuel_type": forms.Select(attrs={"class": "form-select"}),
            "transmission": forms.Select(attrs={"class": "form-select"}),
            "seating_capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "mileage": forms.TextInput(attrs={"class": "form-control"}),
            "launch_year": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "car_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_upcoming": forms.CheckboxInput(attrs={"class": "form-check-input mt-0"}),
            "is_electric": forms.CheckboxInput(attrs={"class": "form-check-input mt-0"}),
        }

    def clean_vin(self):
        vin = self.cleaned_data["vin"].upper()
        qs = Car.objects.filter(vin=vin)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("VIN already exists.")
        return vin

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")
        return stock

    def clean_launch_year(self):
        year = self.cleaned_data["launch_year"]
        current_year = timezone.now().year
        if year < 1950 or year > current_year + 1:
            raise ValidationError("Enter a valid launch year.")
        return year

class CarListingForm(forms.ModelForm):
    class Meta:
        model = CarListing
        fields = ("car", "price", "mileage", "description", "status")
        widgets = {
            "car": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "mileage": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price
class CarListingImageForm(forms.ModelForm):
    class Meta:
        model = CarListingImage
        fields = ("image", "alt")
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "alt": forms.TextInput(attrs={"class": "form-control"}),
        }
    def clean_image(self):
        image = self.cleaned_data["image"]
        if not image:
            raise ValidationError("Image is required.")
        return image
class TestDriveForm(forms.ModelForm):
    class Meta:
        model = TestDrive
        fields = ("listing", "proposed_date", "actual_date", "status", "notes")
        widgets = {
            "listing": forms.Select(attrs={"class": "form-select"}),
            "proposed_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "actual_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_proposed_date(self):
        date = self.cleaned_data["proposed_date"]
        if date < timezone.now().date():
            raise ValidationError("Proposed date cannot be in the past.")
        return date