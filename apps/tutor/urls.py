from django.urls import path, include
from . import views

app_name = 'tutor'

urlpatterns = [
    path('', views.tutor_dashboard_view, name='dashboard'),
]
