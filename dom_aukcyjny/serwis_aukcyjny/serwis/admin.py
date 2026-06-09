from django.contrib import admin
from .models import ProfilUzytkownika, Adres, Uzytkownik, Kategoria, Aukcja, Oferta, Platnosc
# Register your models here.

@admin.register(ProfilUzytkownika)
class ProfilUzytkownikaAdmin(admin.ModelAdmin):
    list_display = ("uzytkownik", "rola")
    list_editable = ["rola"]
    list_filter = ["rola"]

@admin.register(Adres)
class AdresAdmin(admin.ModelAdmin):
    list_display = ("kraj", "miasto", "ulica")
    list_filter = ["miasto", "kraj"]

@admin.register(Uzytkownik)
class UzytkownikAdmin(admin.ModelAdmin):
    list_display = ["uzytkownik"]
    search_fields = ["uzytkownik"]
    readonly_fields = ["data_rejestracji"]

@admin.register(Kategoria)
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ["nazwa"]
    search_fields = ["nazwa"]

@admin.register(Aukcja)
class AukcjaAdmin(admin.ModelAdmin):
    list_display = ["sprzedajacy", "kategoria", "nazwa_produktu", "status"]
    search_fields = ["kategoria", "sprzedajacy", ]
    readonly_fields = ["data_wystawienia", "slug"]
    list_editable = ["status"]


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ["aukcja", "kupujacy", "oferowana_cena"]
    search_fields = ["kupujacy", "aukcja"]
    readonly_fields = ["data_zlozenia_oferty"]

@admin.register(Platnosc)
class PlatnoscAdmin(admin.ModelAdmin):
    list_display = ["aukcja", "platnik"]
    search_fields = ["aukcja", "platnik", ]
    readonly_fields = ["data_platnosc"]