
from django_contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth import login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('order/', views.order, name='order'),

    # Cars
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/update/<int:car_id>/', views.update_car, name='update_car'),
    path('cars/delete/<int:car_id>/', views.delete_car, name='delete_car'),
    path('inventory/', views.inventory, name='inventory'),
    path('upcoming/', views.upcoming_cars, name='upcoming_cars'),
    path('electric/', views.electric_cars, name='electric_cars'),
    path('compare/', views.compare_car, name='compare_cars'),
    path('find/', views.find_new, name='find_new'),
    
    # Used Cars
    path('used/', views.used_car_list, name='used_car_list'),
    path('used/add/', views.add_used_car, name='add_used_car'),

    # News
    path('news/', views.news_list, name='news_list'),
    path('news/add/', views.add_news, name='add_news'),

    # Auth
    path("signup/", views.signup_view, name="signup_view"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)