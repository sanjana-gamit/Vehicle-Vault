from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.text import slugify
import uuid

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.update({
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "role": User.Role.ADMIN,
        })
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to="users/", blank=True, null=True)

    class Role(models.TextChoices):
        BUYER = "Buyer", "Buyer"
        SELLER = "Seller", "Seller"
        DEALER = "Dealer", "Dealer"
        ADMIN = "Admin", "Admin"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER,
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
    preferences = models.JSONField(blank=True, null=True)
    favorite_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.user.role != User.Role.BUYER:
            self.user.role = User.Role.BUYER
            self.user.save(update_fields=["role"])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Buyer | {self.user.email}"


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    dealership_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.user.role != User.Role.SELLER:
            self.user.role = User.Role.SELLER
            self.user.save(update_fields=["role"])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Seller | {self.user.email}"

class CarCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Car(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cars",
        limit_choices_to={"role__in": ["Seller", "Admin"]},
    )

    category = models.ForeignKey(
        CarCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cars",
    )

    vin = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(unique=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ("Petrol", "Petrol"),
            ("Diesel", "Diesel"),
            ("Electric", "Electric"),
            ("Hybrid", "Hybrid"),
        ],
        default="Petrol",
    )
    mileage = models.CharField(max_length=50)
    launch_year = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    car_image = models.ImageField(upload_to="cars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_available = self.stock > 0
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.model}-{self.launch_year}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model}"

class CarListing(models.Model):
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="listings")
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings",
        limit_choices_to={"role__in": ["Seller", "Admin"]},
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)
    mileage = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[("Active", "Active"), ("Sold", "Sold")],
        default="Active",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} | {self.status}"

class CarListingImage(models.Model):
    listing = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="car_listings/")
    alt = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.alt:
            self.alt = self.image.name
        super().save(*args, **kwargs)

class TestDrive(models.Model):
    test_drive_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    listing = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name="test_drives")
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "Buyer"},
        related_name="test_drives",
    )

    proposed_date = models.DateField()
    actual_date = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Confirmed", "Confirmed"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
