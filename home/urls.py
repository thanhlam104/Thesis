
from django.urls import path
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('new/', views.new),
    path('register/', views.register,name='register'),
    path('data-importer/',views.dataImporter, name='data-importer'),
    path('login/',auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('logout/',auth_views.LogoutView.as_view(next_page='/'),name='logout'),
]
