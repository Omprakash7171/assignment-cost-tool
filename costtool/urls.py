"""URLs for the Cost Estimate tab."""
from django.urls import path

from . import views

app_name = 'costtool'

urlpatterns = [
    path('', views.cost_estimate, name='cost_estimate'),
    path('compare/', views.scenario_compare, name='scenario_compare'),
    path('export/csv/', views.csv_export, name='csv_export'),
]
