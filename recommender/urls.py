from django.http import HttpResponse
from . import neo4jRec as rec
from . import views

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User
from django.conf.urls.static import static
from django.conf import settings


def test(request):
    driver = rec.Recommender('bolt://localhost:11003')
    result = driver.byKNN(10)
    return HttpResponse(result.to_json(orient='records'))
urlpatterns = [
    path('test/<name>/',views.project),
    path('create-project/',views.create_project),
    path('clear-files/',views.clear_files)
]