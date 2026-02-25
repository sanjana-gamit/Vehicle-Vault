from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginView, name='login'),
    path('signup/', views.UserSignupView, name='signup'),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("about/", views.about, name="about"),
]