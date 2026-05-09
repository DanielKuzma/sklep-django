from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from sklep_aplikacja.models import Produkt


class ListaProduktowViewTest(TestCase):
    def test_lista_produktow_zwraca_status_200(self):
        response = self.client.get(reverse("lista_produktow"))
        self.assertEqual(response.status_code, 200)

    def test_lista_pokazuje_tylko_aktywne_produkty(self):
        Produkt.objects.create(
            nazwa_produktu="Widoczny produkt",
            cena_produktu=Decimal("10.00"),
            stan_magazynowy=5,
            czy_aktywny=True,
        )
        Produkt.objects.create(
            nazwa_produktu="Ukryty produkt",
            cena_produktu=Decimal("20.00"),
            stan_magazynowy=5,
            czy_aktywny=False,
        )

        response = self.client.get(reverse("lista_produktow"))

        self.assertContains(response, "Widoczny produkt")
        self.assertNotContains(response, "Ukryty produkt")