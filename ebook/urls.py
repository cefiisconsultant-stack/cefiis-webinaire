from django.urls import path
from . import views

urlpatterns = [
    path("", views.vente_ebook, name="vente_ebook"),
    path("verifier-paiement/", views.verifier_paiement, name="verifier_paiement"),
    path("merci/<uuid:token>/", views.page_merci, name="page_merci"),
    path("telecharger/<uuid:token>/", views.telecharger_ebook, name="telecharger_ebook"),
]