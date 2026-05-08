from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.strona_glowna, name = "strona_glowna"),
    path("produkty/", views.lista_produktow, name="lista_produktow"),
    path("test/", views.test_dane, name="test_dane"),
    path("produkty/<int:id_produktu>/", views.szczegoly_produktu, name="szczegoly_produktu"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)