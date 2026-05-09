from decimal import Decimal
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from sklep_aplikacja.models import Klient, Produkt, Zamowienie
from django.test import TestCase


class ZamowienieE2ETest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.user = User.objects.create_user(
            username="klient1",
            password="Test1234!",
            first_name="Jan",
            last_name="Kowalski",
        )
        Klient.objects.create(
            uzytkownik=self.user,
            ulica="Testowa 1",
            kod_pocztowy="00-001",
            miasto="Warszawa",
        )
        self.produkt = Produkt.objects.create(
            nazwa_produktu="Kubek Django",
            cena_produktu=Decimal("39.00"),
            stan_magazynowy=5,
            czy_aktywny=True,
        )

    def tearDown(self):
        self.browser.quit()

    def test_klient_moze_dodac_produkt_do_koszyka(self):
        url = self.live_server_url + reverse("lista_produktow")
        self.browser.get(url)

        self.assertIn("Kubek Django", self.browser.page_source)

        # Ten selektor zależy od HTML-a w Twoim szablonie.
        link = self.browser.find_element(By.LINK_TEXT, "Kubek Django")
        link.click()

        przycisk = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        przycisk.click()

        self.assertIn("Koszyk", self.browser.page_source)

class SkladanieZamowieniaRegresyjneTest(TestCase):
    def test_brak_w_magazynie_nie_tworzy_pustego_zamowienia(self):
        user = User.objects.create_user(username="ala", password="Test1234!")
        Klient.objects.create(
            uzytkownik=user,
            ulica="Testowa 1",
            kod_pocztowy="00-001",
            miasto="Warszawa",
        )
        produkt = Produkt.objects.create(
            nazwa_produktu="Laptop",
            cena_produktu=Decimal("3000.00"),
            stan_magazynowy=2,
            czy_aktywny=True,
        )
        self.client.login(username="ala", password="Test1234!")

        # Próbujemy dodać 5 sztuk produktu, którego mamy tylko 2.
        # Tu zakładamy widok ustawiający ilość. Jeśli go nie masz, użyj
        # innej ścieżki – ważne, żeby koszyk miał za dużą liczbę sztuk.
        session = self.client.session
        session["koszyk"] = {str(produkt.pk): 5}
        session.save()

        # Widok zloz_zamowienie ma @require_POST (lekcja 11.9), więc test musi
        # użyć POST. Wywołanie GET zwróci HTTP 405 i regresja nie zostałaby
        # wykryta.
        response = self.client.post(reverse("zloz_zamowienie"))

        # Powinniśmy wrócić do koszyka z komunikatem.
        self.assertRedirects(response, reverse("koszyk"))
        # I, co najważniejsze, w bazie nie ma żadnego zamówienia.
        self.assertEqual(Zamowienie.objects.count(), 0)
        # Stan magazynowy się nie zmienił.
        produkt.refresh_from_db()
        self.assertEqual(produkt.stan_magazynowy, 2)