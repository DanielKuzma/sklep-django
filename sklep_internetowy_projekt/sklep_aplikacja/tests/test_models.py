from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from sklep_aplikacja.models import Klient, Produkt, Zamowienie, PozycjaZamowienia


class PozycjaZamowieniaModelTest(TestCase):
    def test_suma_liczy_ilosc_razy_cene(self):
        user = User.objects.create_user(username="ala", password="Test1234!")
        klient = Klient.objects.create(uzytkownik=user, miasto="Warszawa")
        produkt = Produkt.objects.create(
            nazwa_produktu="Kubek",
            cena_produktu=Decimal("25.00"),
            stan_magazynowy=10,
        )
        zamowienie = Zamowienie.objects.create(
            klient=klient,
            adres_dostawy="Testowa 1, 00-001 Warszawa",
        )
        pozycja = PozycjaZamowienia.objects.create(
            zamowienie=zamowienie,
            produkt=produkt,
            ilosc=3,
            cena_jednostkowa=Decimal("25.00"),
        )

        self.assertEqual(pozycja.suma(), Decimal("75.00"))