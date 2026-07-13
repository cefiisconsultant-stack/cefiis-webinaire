from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from webinaire.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pourquoi-devenir-consultant/', webinaire_pre_frame_bridge, name="webinaire-pre-frame-bridge"),
    path('inscription-webinaire-confirmé/', webinaire_confirmation, name="webinaire-reservation"),
    path("confirmation-inscription-webinaire/", reservation_webinaire, name="reservation_webinaire"),
    path("inscription-webinaire/", webinaire_page_c, name="webinaire_page_c"),
    path("ebook/", include("ebook.urls")),
    path("formations/", include("formations.urls")),
    path("blog/", include("blog.urls")),          # <-- cette ligne manque actuellement
    path("", include("vitrine.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)