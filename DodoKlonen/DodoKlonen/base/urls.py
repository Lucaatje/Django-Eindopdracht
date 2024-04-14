from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logoutview", views.logoutview, name="logoutview"),
    path("", include('django.contrib.auth.urls')),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password')
]