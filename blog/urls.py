from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.browse_posts, name = 'blog'),
    path('<int:id>/', views.post, name = 'post'),
]
