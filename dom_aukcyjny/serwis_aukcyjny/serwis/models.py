from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime
from django.core.validators import MinValueValidator
from django.utils.text import slugify


# Create your models here.
class ProfilUzytkowniak(models.Model):
    ROLE = [
        ("Klient", "Klient"),
        ("Pracownik", "Pracownik"),
    ]
    uzytkownik = models.OneToOneField(User, on_delete=models.CASCADE)
    rola  = models.CharField(max_length=20, choices = ROLE, default = "Klient")
    
    def __str__(self):
        return f""

class Adres(models.Model):
    ulica = models.CharField(max_length = 255, null = False)
    numer_budynku = models.CharField(max_length = 10, null = False)
    numer_lokalu = models.CharField(max_length = 10, null = True, blank = True)
    kod_pocztowy = models.CharField(max_length = 6, null = False)
    miasto = models.CharField(max_length = 100, null = False)
    kraj = models.CharField(max_length = 100, null = False)

    def __str__(self):
        return f""

class Uzytkownik(models.Model):
    uzytkownik = models.OneToOneField(User, on_delete = models.CASCADE)
    adres = models.ForeignKey(Adres, on_delete = models.CASCADE, name = "uzytkownicy")
    nazwa_uzytkownika = models.CharField(max_length = 80, unique = True, null = False)
    telefon = models.CharField(max_length = 11, null = False)
    data_rejestracji = models.DateField(default=date.today)

    def __str__(self):
        return f""

class Kategoria(models.Model):
    nazwa = models.CharField(null = False, max_length = 100, unique = True)

    def __str__(self):
        return f""
    
class Aukcja(models.Model):
    STATUS = [
        ("Aktywny", "Aktywny"),
        ("Zakonczone", "Zakonczone")
    ]

    sprzedajacy = models.ForeignKey(Uzytkownik, on_delete = models.CASCADE, name = "aukcje")
    kategoria = models.ForeignKey(Kategoria, on_delete = models.SET_NULL, name = "kategorie")
    nazwa_produktu = models.CharField(max_length = 200, null = False)
    cena_wywolawcza = models.FloatField(null = False, validators = [MinValueValidator(0.0)])
    data_wystawienia = models.DateField(auto_now_add=True)
    data_zakonczenia = models.DateField(null = False)
    opis = models.TextField(max_length = 1500 ,null = False, blank = True)
    status = models.CharField(choices = STATUS, default = "Aktywny")
    slug = models.SlugField(blank = True)

    def save(self, *args, **kwargs):
        self.slug= slugify(f"{self.nazwa_produktu} {self.id}")
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f""
    
class Oferta(models.Model):
    aukcja = models.ForeignKey(Aukcja, on_delete = models.CASCADE, name = "aukcja")
    kupujacy = models.ForeignKey(Uzytkownik, on_delete = models.CASCADE, name = "uzytkownik")
    oferowana_cena = models.FloatField(null = False)
    data_zlozenia_oferty = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f""

class Platnosc(models.Model):
    STATUS = [
        ("Zaplacone", "Zaplacone"),
        ("Anulowano", "Anulowano"),
        ("Nie Zaplacone", "Nie Zaplacone")
    ]

    METODA_PLATNOSCI = [
        ("Karta", "Karta"),
        ("Gotowka", "Gotowka")
    ]

    aukcja = models.ForeignKey(Aukcja, on_delete = models.CASCADE, name = "aukcja")
    platnik = models.ForeignKey(Uzytkownik, on_delete = models.CASCADE, name = "uzytkownik")
    status_platnosci = models.CharField(choices = STATUS, default = "Nie Zaplacone")
    cena_koncowa = models.FloatField(null = False)
    metoda_platnosc = models.CharField(choices = METODA_PLATNOSCI, null = False)
    data_platnosc = models.DateTimeField(blank = True)

    def __str__(self):
        return f""

    def save(self, *args, **kwargs):
        if self.status_platnosci == "Zaplacone":
            self.data_platnosc = datetime.now().strftime("%Y-%m-%d %H:%M")
        return super().save(*args, **kwargs)
