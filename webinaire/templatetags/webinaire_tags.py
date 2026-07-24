from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def webinaire_date():
    return settings.WEBINAIRE_DATE_AFFICHAGE


@register.simple_tag
def webinaire_date_iso():
    return settings.WEBINAIRE_DATE_ISO
