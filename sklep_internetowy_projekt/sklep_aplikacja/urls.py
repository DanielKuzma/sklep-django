from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.strona_glowna, name = "strona_glowna"),
    path("produkty/", views.lista_produktow, name="lista_produktow"),
    path("test/", views.test_dane, name="test_dane"),
    path("konto/zamowienia/", views.historia_zamowien, name="historia_zamowien"),
    path("konto/profil/", views.panel_klienta, name="panel_klienta"),
    path("panel-pracownika/", views.panel_pracownika, name="panel_pracownika"),
    path("panel-pracownika/zamowienia/", views.lista_zamowien_pracownik, name="lista_zamowien_pracownik"),
    path("koszyk/", views.koszyk, name="koszyk"),
    path("koszyk/zloz-zamowienie/", views.zloz_zamowienie, name="zloz_zamowienie"),
    path("panel-pracownika/zamowienia/", views.lista_zamowien_pracownik, name="lista_zamowien_pracownik"),
    path("rejestracja/", views.rejestracja_klienta, name="rejestracja_klienta"),

    path("konto/zamowienia/<int:id_zamowienia>/", views.szczegoly_zamowienia, name="szczegoly_zamowienia"),
    path("produkty/<slug:slug>/", views.szczegoly_produktu, name="szczegoly_produktu"),
    path("koszyk/dodaj/<int:id_produktu>/", views.dodaj_do_koszyka, name="dodaj_do_koszyka"),
    path("koszyk/usun/<int:id_produktu>/", views.usun_z_koszyka, name="usun_z_koszyka"),
    path("panel-pracownika/zamowienia/<int:id_zamowienia>/zmien-status/", views.zmien_status_zamowienia, name="zmien_status_zamowienia"),
    path("panel-pracownika/zamowienia/<int:id_zamowienia>/", views.szczegoly_zamowienia_pracownik, name="szczegoly_zamowienia_pracownik"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)