from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logoutview", views.logoutview, name="logoutview"),
    path("", include('django.contrib.auth.urls')),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('add_dodo/', views.add_dodo, name='add_dodo'),
    path('add_update/<str:dodo_name>/', views.add_update, name='add_update'),
    path('update/<int:update_id>/delete/', views.delete_update, name='delete_update'),
    path('update/<int:update_id>/edit/', views.edit_update, name='edit_update'),
    path('newsfeed/', views.newsfeed, name='newsfeed'),
    path('dodo/<str:dodo_name>/', views.dodo_details, name='dodo_details'),
    path('dodo/<str:dodo_name>/mark_as_dead/', views.mark_as_dead, name='mark_as_dead'),
    path('unapproved_dodos/', views.unapproved_dodos, name='unapproved_dodos'),
    path('approve_dodo/<str:dodo_name>/', views.approve_dodo, name='approve_dodo'),
    path('reject_dodo/<str:dodo_name>/', views.reject_dodo, name='reject_dodo'),
    path('dodo/<str:dodo_name>/delete_all_updates/', views.delete_all_updates, name='delete_all_updates')
    ]