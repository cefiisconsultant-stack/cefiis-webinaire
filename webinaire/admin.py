from django.contrib import admin
from .models import *

@admin.register(ReservationWebinaire)
class ReservationWebinaireAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "email", "profession", "date_inscription", "dans_sequence_opera", "niveau_sequence", "niveau_etude")
    search_fields = ("prenom", "nom", "email", "profession")
    list_filter = ("profession", "date_inscription")

# @admin.register(EmailTracking)
# class EmailTrackingAdmin(admin.ModelAdmin):
#     list_display = ("email", "email_name", "opened", "last_opened_at")
    # search_fields = ("")
    # list_filter = ("")

# Register your models here.
