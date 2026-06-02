# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import date, timedelta
from .models import Uzytkownik, Kategoria, Aukcja, Oferta, Platnosc, Adres

class AukcjaLogikaBiznesowaTests(TestCase):
    """Testy sprawdzające logikę modeli i walidację."""

    def setUp(self):
        self.adres = Adres.objects.create(
            kraj="Polska", miasto="Warszawa", ulica="Złota", 
            kod_pocztowy="00-001", numer_budynku="44"
        )
        
        self.user_sprzedawca = User.objects.create_user(username="sprzedawca", password="pwd")
        self.uzytkownik_sprzedawca = Uzytkownik.objects.create(
            uzytkownik=self.user_sprzedawca, adres=self.adres, telefon="123456789"
        )
        
        self.user_kupujacy1 = User.objects.create_user(username="kupujacy1", password="pwd")
        self.uzytkownik_kupujacy1 = Uzytkownik.objects.create(uzytkownik=self.user_kupujacy1)

        self.user_kupujacy2 = User.objects.create_user(username="kupujacy2", password="pwd")
        self.uzytkownik_kupujacy2 = Uzytkownik.objects.create(uzytkownik=self.user_kupujacy2)

        self.kategoria = Kategoria.objects.create(nazwa="Elektronika")
        self.aukcja = Aukcja.objects.create(
            sprzedajacy=self.uzytkownik_sprzedawca,
            kategoria=self.kategoria,
            nazwa_produktu="Konsola PS5",
            cena_wywolawcza=2000.0,
            data_zakonczenia=date.today() + timedelta(days=5),
            status="Aktywny"
        )

    # test generowania sluga
    def test_automatyczne_generowanie_sluga(self):
        self.assertIsNotNone(self.aukcja.slug)
        self.assertTrue(self.aukcja.slug.startswith("konsola-ps5-"))

    # test za niskiej pierwszej oferty
    def test_walidacja_pierwszej_oferty_ponizej_ceny_wywolawczej(self):
        oferta = Oferta(aukcja=self.aukcja, kupujacy=self.user_kupujacy1, oferowana_cena=1900.0)
        with self.assertRaises(ValidationError):
            oferta.clean()

    # test za niskiej kolejnej oferty
    def test_walidacja_kolejnej_oferty_ponizej_ostatniej_oferty(self):
        Oferta.objects.create(aukcja=self.aukcja, kupujacy=self.user_kupujacy1, oferowana_cena=2100.0)
        zla_oferta = Oferta(aukcja=self.aukcja, kupujacy=self.user_kupujacy2, oferowana_cena=2050.0)
        with self.assertRaises(ValidationError):
            zla_oferta.clean()

    # test zamykania aukcji i tworzenia rachunku
    def test_wystawienie_rachunku_i_zamkniecie_aukcji(self):
        Oferta.objects.create(aukcja=self.aukcja, kupujacy=self.user_kupujacy1, oferowana_cena=2500.0)
        self.aukcja.wystaw_rachunek()
        self.aukcja.refresh_from_db()
        
        self.assertEqual(self.aukcja.status, "Zakonczone")
        rachunek = Platnosc.objects.filter(aukcja=self.aukcja).first()
        self.assertIsNotNone(rachunek)
        self.assertEqual(rachunek.cena_koncowa, 2500.0)
        self.assertEqual(rachunek.platnik, self.uzytkownik_kupujacy1)


class AukcjaWidokiTests(TestCase):
    """Testy sprawdzające działanie widoków i adresów URL."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pwd123")
        self.adres = Adres.objects.create(kraj="X", miasto="Y", ulica="Z", kod_pocztowy="00-000", numer_budynku="1")
        self.uzytkownik = Uzytkownik.objects.create(uzytkownik=self.user, adres=self.adres)
        
        self.kategoria = Kategoria.objects.create(nazwa="Książki")
        self.aukcja = Aukcja.objects.create(
            sprzedajacy=self.uzytkownik, kategoria=self.kategoria,
            nazwa_produktu="Django w Praktyce", cena_wywolawcza=50.0,
            data_zakonczenia=date.today() + timedelta(days=2), status="Aktywny"
        )

    # test publicznego dostępu do listy aukcji
    def test_widok_listy_aukcji_dostepny_publicznie(self):
        response = self.client.get(reverse('auction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django w Praktyce")

    # test blokady niezalogowanego użytkownika
    def test_widok_szczegolow_aukcji_wymaga_logowania(self):
        url = reverse('action_detail', kwargs={'slug': self.aukcja.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    # test dostępu do szczegółów po zalogowaniu
    def test_widok_szczegolow_aukcji_po_zalogowaniu(self):
        self.client.login(username="testuser", password="pwd123")
        url = reverse('action_detail', kwargs={'slug': self.aukcja.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)