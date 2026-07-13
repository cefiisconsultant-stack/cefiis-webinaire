from django.shortcuts import render
from formations.models import Offer
from .models import PortfolioItem, EvenementPhoto, Realisation, RealisationImage


def home(request):
    return render(request, "vitrine/home.html", {
        "offers": Offer.objects.filter(is_active=True, categorie="parcours").order_by("order"),
        "evenements": EvenementPhoto.objects.filter(is_active=True),
        "realisations": Realisation.objects.filter(is_active=True).prefetch_related("images"),
    })