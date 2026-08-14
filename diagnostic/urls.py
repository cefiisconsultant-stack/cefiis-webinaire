from django.urls import path

from . import views

app_name = "diagnostic"

urlpatterns = [
    path("", views.quiz, name="quiz"),
    path("enregistrer/", views.enregistrer, name="enregistrer"),
    path("evenement/", views.evenement, name="evenement"),
    path("resultat/<uuid:public_id>/", views.resultat, name="resultat"),
    path("resultat/<uuid:public_id>/avis/", views.enregistrer_avis, name="avis"),
]
