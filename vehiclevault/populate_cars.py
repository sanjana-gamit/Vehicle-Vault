import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vehiclevault.settings")
django.setup()

from cars.models import User, Car, CarCategory, Brand
from django.core.files import File

def populate():
    print("Starting car population script...")

    # 1. Create Admin & Seller if they don't exist
    admin_user, _ = User.objects.get_or_create(
        email="admin@vehiclevault.com",
        defaults={
            "name": "Global Admin",
            "role": User.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True
        }
    )
    if not admin_user.has_usable_password():
        admin_user.set_password("admin123")
        admin_user.save()

    seller_user, _ = User.objects.get_or_create(
        email="seller@vehiclevault.com",
        defaults={
            "name": "Elite Motors",
            "role": User.Role.SELLER,
        }
    )
    if not seller_user.has_usable_password():
        seller_user.set_password("seller123")
        seller_user.save()

    # 2. Create Categories
    categories = ["SUV", "Sedan", "Hatchback", "Luxury", "Electric"]
    cat_objs = {}
    for cat_name in categories:
        cat, _ = CarCategory.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = cat

    # 3. Populate Brands
    brands_data = [
        {"name": "Aston Martin", "logo": "aston-martinlogo.avif"},
        {"name": "Audi", "logo": "audilogo.avif"},
        {"name": "Bentley", "logo": "bentleylogo.avif"},
        {"name": "BMW", "logo": "bmwlogo.avif"},
        {"name": "BYD", "logo": "bydlogo.avif"},
        {"name": "Citroen", "logo": "citroenlogo.avif"},
        {"name": "Ferrari", "logo": "ferrarilogo.avif"},
        {"name": "Force Motors", "logo": "force-motorslogo.avif"},
        {"name": "Honda", "logo": "hondalogo.avif"},
        {"name": "Hyundai", "logo": "hyundailogo.avif"},
        {"name": "Isuzu", "logo": "isuzulogo.avif"},
        {"name": "Jaguar", "logo": "jaguarlogo.avif"},
        {"name": "Jeep", "logo": "jeeplogo.avif"},
        {"name": "Kia", "logo": "kialogo.avif"},
        {"name": "Lamborghini", "logo": "lamborghinilogo.avif"},
        {"name": "Land Rover", "logo": "land-roverlogo.avif"},
        {"name": "Lexus", "logo": "lexuslogo.avif"},
        {"name": "Lotus", "logo": "lotuslogo.avif"},
        {"name": "Mahindra", "logo": "mahindralogo.avif"},
        {"name": "Maruti Suzuki", "logo": "marutilogo.avif"},
        {"name": "Maserati", "logo": "maseratilogo.avif"},
        {"name": "McLaren", "logo": "mclarenlogo.avif"},
        {"name": "Mercedes-Benz", "logo": "mercedes-benzlogo.avif"},
        {"name": "MG", "logo": "mglogo.avif"},
        {"name": "Mini", "logo": "minilogo.avif"},
        {"name": "Nissan", "logo": "nissanlogo.avif"},
        {"name": "Porsche", "logo": "porschelogo.avif"},
        {"name": "Renault", "logo": "renaultlogo.avif"},
        {"name": "Rolls-Royce", "logo": "rolls-roycelogo.avif"},
        {"name": "Skoda", "logo": "skodalogo.avif"},
        {"name": "Tata", "logo": "tatalogo.avif"},
        {"name": "Tesla", "logo": "teslalogo.avif"},
        {"name": "Toyota", "logo": "toyotalogo.avif"},
        {"name": "Vinfast", "logo": "vinfastlogo.avif"},
        {"name": "Volkswagen", "logo": "volkswagenlogo.avif"},
        {"name": "Volvo", "logo": "volvologo.avif"},
    ]

    static_images_path = os.path.join("static", "images")

    for b_data in brands_data:
        brand, created = Brand.objects.get_or_create(name=b_data["name"])
        if created or not brand.logo:
            logo_path = os.path.join(static_images_path, b_data["logo"])
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    brand.logo.save(b_data["logo"], File(f), save=True)
                print(f"Updated Brand Logo: {brand.name}")
            else:
                print(f"Logo not found for: {b_data['name']} at {logo_path}")
        else:
            print(f"Brand already exists: {b_data['name']}")

    # 4. Define Car Data based on static images
    cars_data = [
        {
            "brand": "Audi", "model": "Q8 e-tron", "cat": "Electric", "img": "Audi.jpg", 
            "price": 11400000, "year": 2025, "hp": 408, "torque": 664, "speed": 210, "acc": 5.6,
            "engine": "Dual Motor Electric", "safety": "5 Star"
        },
        {
            "brand": "BMW", "model": "M4 Competition", "cat": "Luxury", "img": "BMW.jpg", 
            "price": 15300000, "year": 2025, "hp": 510, "torque": 650, "speed": 250, "acc": 3.5,
            "engine": "3.0L Straight-6 Twin-Turbo", "safety": "5 Star"
        },
        {
            "brand": "Kia", "model": "EV6", "cat": "Electric", "img": "Kia.jpg", 
            "price": 6000000, "year": 2025, "hp": 320, "torque": 605, "speed": 192, "acc": 5.2,
            "engine": "77.4 kWh Battery Pack", "safety": "5 Star"
        },
        {
            "brand": "MG", "model": "Cyberster", "cat": "Luxury", "img": "MG.jpg", 
            "price": 5500000, "year": 2026, "hp": 536, "torque": 725, "speed": 200, "acc": 3.2,
            "engine": "Electric AWD", "safety": "N/A"
        },
        {
            "brand": "Mahindra", "model": "XUV700", "cat": "SUV", "img": "Mahindra.jpg", 
            "price": 2600000, "year": 2025, "hp": 200, "torque": 380, "speed": 190, "acc": 9.2,
            "engine": "2.0L mStallion Turbo Petrol", "safety": "5 Star"
        },
        {
            "brand": "Mercedes-Benz", "model": "AMG SL63", "cat": "Luxury", "img": "Mercedes.jpg", 
            "price": 23500000, "year": 2025, "hp": 585, "torque": 800, "speed": 315, "acc": 3.6,
            "engine": "4.0L V8 Biturbo", "safety": "N/A"
        },
        {
            "brand": "Nissan", "model": "Magnite Kuro", "cat": "SUV", "img": "Nissan.jpg", 
            "price": 980000, "year": 2025, "hp": 100, "torque": 160, "speed": 170, "acc": 10.5,
            "engine": "1.0L Turbo Petrol", "safety": "4 Star"
        },
        {
            "brand": "Maruti Suzuki", "model": "Swift", "cat": "Hatchback", "img": "Swift.jpg", 
            "price": 850000, "year": 2025, "hp": 89, "torque": 113, "speed": 165, "acc": 11.5,
            "engine": "1.2L DualJet Dual VVT", "safety": "3 Star"
        },
        {
            "brand": "Tata", "model": "Safari Dark", "cat": "SUV", "img": "Tata.jpg", 
            "price": 2700000, "year": 2025, "hp": 170, "torque": 350, "speed": 185, "acc": 10.2,
            "engine": "2.0L Kryotec Turbocharged Diesel", "safety": "5 Star"
        },
        {
            "brand": "Honda", "model": "Civic Type R", "cat": "Luxury", "img": "honda.jpg", 
            "price": 4500000, "year": 2025, "hp": 315, "torque": 420, "speed": 272, "acc": 5.4,
            "engine": "2.0L VTEC Turbocharged I4", "safety": "5 Star"
        },
    ]

    for data in cars_data:
        vin_prefix = f"VV-{data['brand'][:2].upper()}"
        
        car, created = Car.objects.get_or_create(
            brand=data["brand"],
            model=data["model"],
            defaults={
                "seller": seller_user,
                "category": cat_objs[data["cat"]],
                "vin": f"{vin_prefix}-{random.randint(1000, 9999)}",
                "price": data["price"],
                "fuel_type": "Electric" if data["cat"] == "Electric" else "Petrol",
                "transmission": "Automatic",
                "launch_year": data["year"],
                "stock": 5,
                "horsepower": data["hp"],
                "torque": data["torque"],
                "top_speed": data["speed"],
                "acceleration_0_100": data["acc"],
                "engine_details": data["engine"],
                "safety_rating": data["safety"],
                "three_d_model_url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
            }
        )

        if created or not car.car_image:
            img_path = os.path.join(static_images_path, data["img"])
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    car.car_image.save(data["img"], File(f), save=True)
                print(f"Updated Image for {car}")
            else:
                print(f"Image not found for: {car} at {img_path}")
        else:
            print(f"Skipped {car} (already exists with image)")

    print("Population complete.")

if __name__ == "__main__":
    populate()
