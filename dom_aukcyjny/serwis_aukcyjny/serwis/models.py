from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from datetime import date, timezone

# Create your models here.
class ProfilUzytkownika(models.Model):
    ROLE = [
        ("Klient", "Klient"),
        ("Pracownik", "Pracownik"),
    ]
    uzytkownik = models.OneToOneField(User, on_delete=models.CASCADE)
    rola  = models.CharField(max_length=20, choices = ROLE, default = "Klient")

    class Meta:
        verbose_name = "Profil Użytkownika"
        verbose_name_plural = "Profile Użytkowników"

    def __str__(self):
        return f"{self.uzytkownik} {self.rola}"

class Adres(models.Model):
    kraj = models.CharField(max_length = 100, null = False)
    miasto = models.CharField(max_length = 100, null = False)
    ulica = models.CharField(max_length = 255, null = False)
    kod_pocztowy = models.CharField(max_length = 6, null = False)
    numer_budynku = models.CharField(max_length = 10, null = False)
    numer_lokalu = models.CharField(max_length = 10, null = True, blank = True)

    class Meta:
        verbose_name = "Adres"
        verbose_name_plural = "Adresy"

    def __str__(self):
        return f"{self.kraj} {self.miasto} {self.ulica}"

class Uzytkownik(models.Model):
    uzytkownik = models.OneToOneField(User, on_delete = models.CASCADE)
    adres = models.ForeignKey(Adres, on_delete = models.SET_NULL, related_name = "uzytkownicy", null = True, blank=True)
    telefon = models.CharField(max_length = 11, blank = True )
    data_rejestracji = models.DateField(default=date.today)

    class Meta:
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def __str__(self):
        return f"{self.uzytkownik}"

class Kategoria(models.Model):
    nazwa = models.CharField(null = False, max_length = 100, unique = True)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return f"{self.nazwa}"
    
class Aukcja(models.Model):
    STATUS = [
        ("Aktywny", "Aktywny"),
        ("Zakonczone", "Zakonczone"),
    ]

    sprzedajacy = models.ForeignKey(Uzytkownik, on_delete = models.CASCADE, related_name = "aukcje")
    kategoria = models.ForeignKey(Kategoria, null = True, blank = True, on_delete = models.SET_NULL, related_name = "kategorie")
    nazwa_produktu = models.CharField(max_length = 200, null = False)
    cena_wywolawcza = models.FloatField(null = False, validators = [MinValueValidator(0.0)])
    data_wystawienia = models.DateField(auto_now_add=True)
    data_zakonczenia = models.DateField(null = False)
    opis = models.TextField(max_length = 1500 ,null = False, blank = True)
    status = models.CharField(choices = STATUS, default = "Aktywny")
    image = models.ImageField(upload_to = "auction_image", default = "default/no-image-icon.png")
    slug = models.SlugField(blank = True)

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs) 
            self.slug = slugify(f"{self.nazwa_produktu}-{self.id}")
            self.save() 
        else:
            super().save(*args, **kwargs) # Zwykły zapis dla edycji
    
    class Meta:
        verbose_name = "Aukcja"
        verbose_name_plural = "Aukcje"

    def wystaw_rachunek(self):
        # Upewniamy się, że aukcja jest wciąż aktywna
        if self.status == "Aktywny":
            # Szukamy najwyższej oferty
            najwyzsza_oferta = self.oferty.order_by("-oferowana_cena").first()
            
            # Jeśli ktoś zalicytował, tworzymy rachunek (Platnosc)
            if najwyzsza_oferta:
                # Import wewnątrz funkcji, żeby uniknąć błędu "circular import"
                from .models import Platnosc 
                Platnosc.objects.create(
                    aukcja=self,
                    platnik=najwyzsza_oferta.kupujacy.uzytkownik,
                    status_platnosci="Nie Zaplacone",
                    cena_koncowa=najwyzsza_oferta.oferowana_cena,
                    # metoda_platnosc celowo pusta - klient ją wybierze!
                )
            
            # Zmieniamy status aukcji na zakończoną
            self.status = "Zakonczone"
            self.save()

    def __str__(self):
        return f"{self.sprzedajacy}, {self.kategoria}, {self.nazwa_produktu}, {self.status}"
    
class Oferta(models.Model):
    aukcja = models.ForeignKey(Aukcja, on_delete = models.SET_NULL, null = True, blank = True, related_name = "oferty")
    kupujacy = kupujacy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="zlozone_oferty")
    oferowana_cena = models.FloatField(null = False)
    data_zlozenia_oferty = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Oferty"

    def clean(self):
        super().clean()
        
        if self.aukcja and self.oferowana_cena is not None:    
        
            last_offer = self.aukcja.oferty.order_by("-data_zlozenia_oferty").first()
            if last_offer:
                if self.oferowana_cena <= last_offer.oferowana_cena:
                    raise ValidationError({
                        "oferowana_cena": f"Oferta musi być wyższa niż ostatnia złożona oferta ({last_offer.oferowana_cena})."
                    })
            else:
                if hasattr(self.aukcja, 'cena_wywolawcza') and self.oferowana_cena <= self.aukcja.cena_wywolawcza:
                    raise ValidationError({
                        "oferowana_cena": f"Pierwsza oferta musi być wyższa niż cena wywoławcza ({self.aukcja.cena_wywolawcza})."
                    })

    def __str__(self):
        return f"{self.aukcja} {self.kupujacy} {self.oferowana_cena}"
    

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

    aukcja = models.ForeignKey(Aukcja, on_delete=models.CASCADE, related_name="platnosci")
    platnik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name="dokonane_platnosci")
    status_platnosci = models.CharField(max_length=50, choices = STATUS, default = "Nie Zaplacone")
    cena_koncowa = models.FloatField(null = False)
    metoda_platnosc = models.CharField(max_length=50, choices=METODA_PLATNOSCI, null=True, blank=True)
    data_platnosc = models.DateTimeField(blank = True, null = True)

    def __str__(self):
        return f"{self.aukcja} {self.platnik}"

    class Meta:
        verbose_name = "Płatność"
        verbose_name_plural = "Płatności"

    def save(self, *args, **kwargs):
        if self.status_platnosci == "Zaplacone":
            self.data_platnosc = datetime.now().strftime("%Y-%m-%d %H:%M")
        return super().save(*args, **kwargs)
