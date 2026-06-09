from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from sklep_aplikacja.models import Produkt


class KoszykTest(TestCase):
    def test_dodanie_produktu_do_koszyka_zapisuje_sesje(self):
        produkt = Produkt.objects.create(
            nazwa_produktu="Notes",
            cena_produktu=Decimal("15.00"),
            stan_magazynowy=20,
            czy_aktywny=True,
        )

        response = self.client.post(reverse("dodaj_do_koszyka", args=[produkt.pk]))

        self.assertRedirects(response, reverse("koszyk"))
        self.assertIn(str(produkt.pk), self.client.session["koszyk"])