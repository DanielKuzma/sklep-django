# root root
from django.contrib import admin
from .models import PozycjaZamowienia, Zamowienie, Produkt, Klient, ProfilUzytkownika
# Register your models here.

@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    list_display = ("nazwa_produktu", "cena_produktu", "stan_magazynowy", "czy_aktywny")
    list_filter = ("czy_aktywny",)
    search_fields = ("nazwa_produktu", "opis")
    list_editable = ("cena_produktu", "stan_magazynowy", "czy_aktywny")


@admin.register(Klient)
class KlientAdmin(admin.ModelAdmin):
    list_display = ("uzytkownik", "telefon", "miasto")
    search_fields = ("uzytkownik__email", "uzytkownik__last_name", "telefon")


class PozycjaInline(admin.TabularInline):
    model = PozycjaZamowienia
    extra = 0


@admin.register(Zamowienie)
class ZamowienieAdmin(admin.ModelAdmin):
    list_display = ("id", "klient", "data_zamowienia", "status", "wartosc_zamowienia")
    list_filter = ("status", "data_zamowienia")
    search_fields = ("klient__uzytkownik__email", "id")
    list_editable = ("status",)
    inlines = [PozycjaInline]
    readonly_fields = ("data_zamowienia",)


@admin.register(ProfilUzytkownika)
class ProfilUzytkownikaAdmin(admin.ModelAdmin):
    list_display = ("uzytkownik", "rola")
    list_filter = ("rola",)


@admin.register(PozycjaZamowienia)
class PozycjaZamowieniaAdmin(admin.ModelAdmin):
    list_display = ("zamowienie", "produkt", "ilosc", "cena_jednostkowa")