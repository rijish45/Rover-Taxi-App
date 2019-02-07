from django.urls import path

from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('driver/register', views.driver_register, name='driver_register'),
    path('driver/update_info', views.driver_update_info, name='driver_update_info'),
]
