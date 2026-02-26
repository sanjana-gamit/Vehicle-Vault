from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('login/', views.UserLoginView, name='login'),
    path('signup/', views.UserSignupView, name='signup'),
    path("logout",views.LogoutViewCustom, name='logout'),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("about/", views.about, name="about"),
    
    # Dashboards
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/seller/", views.seller_dashboard, name="seller_dashboard"),
    path("dashboard/buyer/", views.buyer_dashboard, name="buyer_dashboard"),

    # User Management
    path("manage-users/", views.UserManageListView, name="manage_users"),
    path("manage-users/delete/<str:user_id>/", views.UserDeleteView, name="forced_delete_user"),
]