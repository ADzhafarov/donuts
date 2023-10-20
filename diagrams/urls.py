from django.urls import path
from . import views

urlpatterns = [
    path("", views.donuts, name="donuts"),
]