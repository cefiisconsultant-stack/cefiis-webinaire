from django.urls import path
from . import views

urlpatterns = [
    path("", views.offres, name="offres"),
    path("lead/", views.creer_lead, name="creer_lead"),
]