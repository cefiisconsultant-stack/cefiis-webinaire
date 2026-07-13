from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste, name="blog_liste"),
    path("<slug:slug>/", views.detail, name="blog_detail"),
]