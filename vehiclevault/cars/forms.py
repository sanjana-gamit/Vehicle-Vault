from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import (
    Dealer,
    Car,
    UsedCar,
    Review,
    News,
    CarLoan,
    CarValuation
)

User = get_user_model()


# =========================
# USER REGISTRATION FORM
# =========================
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'city',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


# =========================
# DEALER FORM
# =========================
class DealerForm(forms.ModelForm):
    class Meta:
        model = Dealer
        fields = [
            'dealer_name',
            'phone',
            'city',
            'dealer_image',
        ]


# =========================
# NEW CAR FORM
# =========================
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand',
            'model',
            'price',
            'fuel_type',
            'transmission',
            'mileage',
            'launch_year',
            'car_image',
        ]

        widgets = {
            'brand': forms.TextInput(attrs={'placeholder': 'Brand name'}),
            'model': forms.TextInput(attrs={'placeholder': 'Model name'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price'}),
            'launch_year': forms.NumberInput(attrs={'placeholder': 'Year'}),
        }


# =========================
# USED CAR FORM
# =========================
class UsedCarForm(forms.ModelForm):
    class Meta:
        model = UsedCar
        fields = [
            'car',
            'year',
            'kilometers',
            'price',
            'status',
            'used_car_image',
        ]

        widgets = {
            'year': forms.NumberInput(attrs={'placeholder': 'Manufacture year'}),
            'kilometers': forms.NumberInput(attrs={'placeholder': 'KM driven'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Selling price'}),
        }


# =========================
# REVIEW FORM
# =========================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'rating',
            'comment',
        ]

        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your review...'
            }),
        }


# =========================
# NEWS FORM
# =========================
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title',
            'content',
            'category',
            'news_image',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'News title'}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }


# =========================
# CAR LOAN FORM
# =========================
class CarLoanForm(forms.ModelForm):
    class Meta:
        model = CarLoan
        fields = [
            'loan_amount',
            'tenure',
        ]

        widgets = {
            'loan_amount': forms.NumberInput(attrs={'placeholder': 'Loan amount'}),
            'tenure': forms.NumberInput(attrs={'placeholder': 'Tenure (months)'}),
        }


# =========================
# CAR VALUATION FORM
# =========================
class CarValuationForm(forms.ModelForm):
    class Meta:
        model = CarValuation
        fields = [
            'year',
        ]

        widgets = {
            'year': forms.NumberInput(attrs={'placeholder': 'Car year'}),
        }


# =========================
# SIGNUP FORM
# =========================
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # hash the password
        if commit:
            user.save()
        return user