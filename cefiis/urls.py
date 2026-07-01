"""
URL configuration for cefiis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webinaire.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pourquoi-devenir-consultant/', webinaire_pre_frame_bridge, name="webinaire-pre-frame-bridge"), 
    path('inscription-webinaire/', webinaire_page, name="webinaire-reservation-page"),
    path('inscription-webinaire-confirmé/', webinaire_confirmation, name="webinaire-reservation"),
    path("confirmation-inscription-webinaire/", reservation_webinaire, name="reservation_webinaire"),
    # path("email/open/", email_open, name="email_open"),
]
