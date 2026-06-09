from decimal import Decimal
from .models import Produkt


class Koszyk:
    KLUCZ_SESJI = "koszyk"

    def __init__(self, request):
        # request.session działa podobnie do słownika.
        self.sesja = request.session
        # Jeśli koszyk nie istnieje w sesji, zaczynamy od pustego słownika.
        self.koszyk = self.sesja.get(self.KLUCZ_SESJI, {})

    def dodaj(self, id_produktu, ilosc=1):
        # Klucze w sesji zapisujemy jako tekst, bo dane sesji muszą być serializowalne.
        klucz = str(id_produktu)
        self.koszyk[klucz] = self.koszyk.get(klucz, 0) + ilosc
        self._zapisz()

    def usun(self, id_produktu):
        klucz = str(id_produktu)
        if klucz in self.koszyk:
            del self.koszyk[klucz]
            self._zapisz()

    def wyczysc(self):
        self.sesja[self.KLUCZ_SESJI] = {}
        # modified=True mówi Django, że sesja została zmieniona i trzeba ją zapisać.
        self.sesja.modified = True

    def _zapisz(self):
        self.sesja[self.KLUCZ_SESJI] = self.koszyk
        self.sesja.modified = True

    def pozycje(self):
        ids = [int(k) for k in self.koszyk.keys()]
        produkty = Produkt.objects.filter(pk__in=ids)
        wynik = []
        for p in produkty:
            ilosc = self.koszyk[str(p.pk)]
            wynik.append({
                "produkt": p,
                "ilosc": ilosc,
                "suma": Decimal(p.cena_produktu) * ilosc,
            })
        return wynik

    def suma(self):
        return sum((poz["suma"] for poz in self.pozycje()), Decimal("0.00"))

    def liczba_sztuk(self):
        return sum(self.koszyk.values())