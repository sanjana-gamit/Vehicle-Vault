from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.HomeView, name="home"),

    # Static pages
    path("find-new/", views.find_new, name="find_new"),
    path("news/", views.news_list, name="news_list"),
    path("order/", views.order, name="order"),

    # Cars
    path("all_cars/", views.CarsListView, name="all_cars"),
    path("add/", views.CarCreateView, name="add"),
    path("cars/<str:vin>/edit/", views.CarUpdateView, name="car_edit"),
    path("cars/<str:vin>/delete/", views.CarDeleteView, name="car_delete"),
    path("cars/<str:vin>/category/", views.CarCategoryView, name="car_category"),
    # Compare
    path("compare/", views.compare_cars, name="compare_cars"),
    path("compare/add/<int:car_id>/", views.add_to_compare, name="add_to_compare"),
    path("compare/remove/<int:car_id>/", views.remove_from_compare, name="remove_from_compare"),

    # Test drives
    path("testdrives/", views.TestDrivesView, name="test_drives"),
]