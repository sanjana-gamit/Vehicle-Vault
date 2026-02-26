from django.urls import path
from . import views

app_name = "cars"

urlpatterns = [
    # Home
    path("", views.HomeView, name="home"),

    # Static pages
    path("find-new/", views.find_new, name="find_new"),

    # Cars
    path("cars/", views.CarsListView, name="all_cars"),
    path("cars/all_cars/", views.CarsListView, name="all_cars_alias"),
    path("cars/used-cars/", views.UsedCarsListView, name="used_cars"),
    path("cars/inventory/", views.InventoryListView, name="inventory"),
    path("cars/upcoming-cars/", views.UpcomingCarsListView, name="upcoming_cars"),
    path("cars/electric-cars/", views.ElectricCarsListView, name="electric_cars"),
    path("cars/new-cars/", views.NewCarsListView, name="new_cars"),
    path("cars/<str:vin>/", views.CarDetailView, name="car_detail"),
    path("add/", views.CarCreateView, name="add"),
    path("cars/<str:vin>/edit/", views.CarUpdateView, name="car_edit"),
    path("cars/<str:vin>/delete/", views.CarDeleteView, name="car_delete"),
    path("category/<str:category_name>/", views.CarCategoryView, name="car_category"),
    # Compare
    path("compare/", views.compare_cars, name="compare_cars"),
    path("compare/add/<int:car_id>/", views.add_to_compare, name="add_to_compare"),
    path("compare/remove/<int:car_id>/", views.remove_from_compare, name="remove_from_compare"),

    # Test drives
    path("testdrives/", views.TestDrivesView, name="test_drives"),
    path("testdrives/update/<uuid:drive_id>/<str:status>/", views.UpdateTestDriveStatusView, name="update_test_drive_status"),
]