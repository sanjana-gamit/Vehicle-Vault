import os
import django
import shutil
import uuid

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vehiclevault.settings")
django.setup()

from django.contrib.auth import get_user_model
from cars.models import Car, CarCategory

User = get_user_model()

def populate():
    # Create a default seller user to own these cars
    seller, created = User.objects.get_or_create(
        email="admin@vehiclevault.com",
        defaults={"name": "Admin Seller"}
    )
    if created:
        seller.set_password("admin123")
        
    # Ensure role is set up properly bypass any save overrides
    seller.role = "Seller"
    seller.save()
    print("Ensured default seller admin@vehiclevault.com exists")

    # Create default category
    category, _ = CarCategory.objects.get_or_create(name="SUV")

    cars_data = [
        {"brand": "Toyota", "model": "Fortuner", "price": 3500000, "image": "logo.jpg"},
        {"brand": "Hyundai", "model": "Creta", "price": 1200000, "image": "download.jpg"},
        {"brand": "Honda", "model": "City", "price": 1100000, "image": "honda.jpg"},
        {"brand": "Maruti Suzuki", "model": "Swift", "price": 600000, "image": "swift.jpg"},
        {"brand": "Mahindra", "model": "XUV700", "price": 1800000, "image": "Mahindra.jpg"},
        {"brand": "Kia", "model": "Seltos", "price": 1500000, "image": "Kia.jpg"},
        {"brand": "BMW", "model": "X5", "price": 7500000, "image": "BMW.jpg"},
        {"brand": "Audi", "model": "Q7", "price": 8000000, "image": "Audi.jpg"},
        {"brand": "Mercedes", "model": "GLE", "price": 8500000, "image": "Mercedes.jpg"},
        {"brand": "Tata", "model": "Harrier", "price": 1600000, "image": "Tata.jpg"},
        {"brand": "MG", "model": "Hector", "price": 1700000, "image": "MG.jpg"},
        {"brand": "Nissan", "model": "Kicks", "price": 1400000, "image": "Nissan.jpg"},
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_img_dir = os.path.join(base_dir, "static", "images")
    media_cars_dir = os.path.join(base_dir, "media", "cars")

    if not os.path.exists(media_cars_dir):
        os.makedirs(media_cars_dir, exist_ok=True)

    for data in cars_data:
        vin = f"VIN{uuid.uuid4().hex[:8].upper()}"
        
        # Check if car already exists
        if Car.objects.filter(brand=data["brand"], model=data["model"]).exists():
            print(f"Skipping {data['brand']} {data['model']}, already exists.")
            continue
            
        car = Car(
            seller=seller,
            category=category,
            vin=vin,
            brand=data["brand"],
            model=data["model"],
            price=data["price"],
            mileage="15 kmpl",
            launch_year=2024,
            stock=5,
            is_available=True
        )
        
        # Move image from static to media so Django ImageField can serve it properly
        static_img_path = os.path.join(static_img_dir, data["image"])
        media_img_path = os.path.join(media_cars_dir, data["image"])
        
        if os.path.exists(static_img_path):
            shutil.copy2(static_img_path, media_img_path)
            car.car_image = f"cars/{data['image']}"
            
        car.save()
        print(f"Added {data['brand']} {data['model']}")

    print("Database population complete!")

if __name__ == "__main__":
    populate()
