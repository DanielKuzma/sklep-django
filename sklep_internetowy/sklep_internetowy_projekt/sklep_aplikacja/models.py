from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class ProfilUzytkownika(models.Model):
    ROLE = [
        ("klient", "Klient"),
        ("pracownik", "Pracownik"),
    ]

    # OneToOneField oznacza relację 1 do 1: jeden User ma jeden profil.
    # CASCADE usuwa profil, gdy usuniemy powiązanego użytkownika.
    uzytkownik = models.OneToOneField(User, on_delete=models.CASCADE)
    rola = models.CharField(max_length=20, choices=ROLE, default="klient")

    def __str__(self):
        return f"{self.uzytkownik.username} ({self.rola})"


class Klient(models.Model):
    uzytkownik = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=30, blank=True)
    ulica = models.CharField(max_length=150, blank=True)
    miasto = models.CharField(max_length=100, blank=True)
    kod_pocztowy = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.uzytkownik.first_name} {self.uzytkownik.last_name}"

class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nazwa

class Produkt(models.Model):
    nazwa_produktu = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    kategoria = models.ForeignKey(
        Kategoria,
        on_delete=models.PROTECT,
        related_name="produkty",
        null=True,
        blank=True,
    )
    opis = models.TextField(blank=True)
    cena_produktu = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stan_magazynowy = models.PositiveIntegerField(default=0)
    czy_aktywny = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Jeżeli przy zapisie slug jest pusty, generujemy go z nazwy.
        if not self.slug:
            self.slug = slugify(self.nazwa_produktu)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nazwa_produktu


class Zamowienie(models.Model):
    STATUSY = [
        ("nowe", "Nowe"),
        ("oplacone", "Opłacone"),
        ("wyslane", "Wysłane"),
        ("zrealizowane", "Zrealizowane"),
        ("anulowane", "Anulowane"),
    ]

    # PROTECT chroni historię zamówień przed przypadkowym usunięciem klienta.
    klient = models.ForeignKey(Klient, on_delete=models.PROTECT, related_name="zamowienia")
    data_zamowienia = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSY, default="nowe")
    adres_dostawy = models.CharField(max_length=255)
    wartosc_zamowienia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"Zamówienie #{self.id} ({self.status})"


class PozycjaZamowienia(models.Model):
    # related_name="pozycje" pozwala pisać: zamowienie.pozycje.all()
    zamowienie = models.ForeignKey(Zamowienie, on_delete=models.CASCADE, related_name="pozycje")
    produkt = models.ForeignKey(Produkt, on_delete=models.PROTECT)
    ilosc = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    cena_jednostkowa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def suma(self):
        return self.ilosc * self.cena_jednostkowa

    def __str__(self):
        return f"{self.produkt.nazwa_produktu} x {self.ilosc}"
    
