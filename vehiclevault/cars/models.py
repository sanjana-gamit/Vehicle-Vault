from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# USER / ADMIN
# =========================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('dealer', 'Dealer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='users/', null=True, blank=True)

    def __str__(self):
        return self.username


# =========================
# DEALER
# =========================
class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    dealer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    approved = models.BooleanField(default=False)
    dealer_image = models.ImageField(upload_to='dealers/', null=True, blank=True)

    def __str__(self):
        return self.dealer_name


# =========================
# CAR (NEW CARS)
# =========================
class Car(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20)
    transmission = models.CharField(max_length=20)
    mileage = models.CharField(max_length=20)
    launch_year = models.IntegerField()
    car_image = models.ImageField(upload_to='cars/new/', null=True, blank=True)
    is_upcoming = models.BooleanField(default=False)
    is_electric = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.model}"


# =========================
# USED CAR
# =========================
class UsedCar(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('sold', 'Sold'),
    )

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='used_versions')
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='used_cars')
    year = models.IntegerField()
    kilometers = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    used_car_image = models.ImageField(upload_to='cars/used/', null=True, blank=True)

    def __str__(self):
        return f"Used {self.car} ({self.year})"


# =========================
# REVIEW
# =========================
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} - {self.rating}⭐"


# =========================
# NEWS
# =========================
class News(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_posts')
    title = models.CharField(max_length=150)
    content = models.TextField()
    category = models.CharField(max_length=50)
    published_date = models.DateTimeField(auto_now_add=True)
    news_image = models.ImageField(upload_to='news/', null=True, blank=True)

    def __str__(self):
        return self.title


# =========================
# CAR LOAN
# =========================
class CarLoan(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='car_loans')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField(help_text="Tenure in months")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Loan ₹{self.loan_amount} - {self.status}"


# =========================
# CAR VALUATION
# =========================
class CarValuation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='car_valuations')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='valuations')
    year = models.IntegerField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.car} - ₹{self.estimated_price}"