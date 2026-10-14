"""URLs for the Immigration tab."""
from django.urls import path

from . import views

app_name = 'reference'

urlpatterns = [
    path('', views.immigration, name='immigration'),
]
