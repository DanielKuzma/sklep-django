from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from sklep_aplikacja.models import ProfilUzytkownika, Klient, Produkt, Zamowienie, PozycjaZamowienia
from datetime import datetime
from decimal import Decimal


class Command(BaseCommand):
    help = "Ładuje dane demonstracyjne sklepu"

    def handle(self, *args, **options):
        self.stdout.write("Tworzenie użytkowników...")
        klienci_data = [
            ("jan.kowalski", "jan.kowalski@example.com", "Jan", "Kowalski",
             "500100200", "ul. Kwiatowa 12", "Warszawa", "00-001"),
            ("anna.nowak", "anna.nowak@example.com", "Anna", "Nowak",
             "501200300", "ul. Leśna 5", "Kraków", "30-002"),
            ("piotr.wisniewski", "piotr.wisniewski@example.com", "Piotr", "Wiśniewski",
             "502300400", "ul. Słoneczna 8", "Poznań", "60-003"),
            ("maria.zielinska", "maria.zielinska@example.com", "Maria", "Zielińska",
             "503400500", "ul. Ogrodowa 21", "Gdańsk", "80-004"),
            ("tomasz.wojcik", "tomasz.wojcik@example.com", "Tomasz", "Wójcik",
             "504500600", "ul. Lipowa 3", "Wrocław", "50-005"),
        ]

        for username, email, imie, nazwisko, tel, ulica, miasto, kod in klienci_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": imie, "last_name": nazwisko},
            )
            if created:
                user.set_password("Demo1234!")
                user.save()
            ProfilUzytkownika.objects.get_or_create(uzytkownik=user, defaults={"rola": "klient"})
            Klient.objects.get_or_create(
                uzytkownik=user,
                defaults={"telefon": tel, "ulica": ulica, "miasto": miasto, "kod_pocztowy": kod},
            )

        pracownicy_data = [
            ("pracownik1", "pracownik1@sklep.pl", "Ewa", "Kaczmarek"),
            ("pracownik2", "pracownik2@sklep.pl", "Michał", "Lewandowski"),
        ]
        for username, email, imie, nazwisko in pracownicy_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email, "first_name": imie, "last_name": nazwisko,
                    "is_staff": True,
                },
            )
            if created:
                user.set_password("Demo1234!")
                user.save()
            ProfilUzytkownika.objects.get_or_create(uzytkownik=user, defaults={"rola": "pracownik"})

        self.stdout.write("Tworzenie produktów...")
        produkty_data = [
            ("Klawiatura mechaniczna", "Klawiatura przewodowa z podświetleniem", "249.99", 35),
            ("Mysz bezprzewodowa", "Ergonomiczna mysz do pracy i gier", "89.90", 60),
            ("Monitor 27 cali", "Monitor IPS 27 cali Full HD", "749.00", 18),
            ("Laptop 15 cali", "Laptop biurowy z dyskiem SSD", "3299.00", 7),
            ("Słuchawki Bluetooth", "Bezprzewodowe słuchawki nauszne", "199.99", 42),
            ("Kabel USB-C", "Kabel USB-C 1 m", "29.99", 120),
            ("Powerbank 20000 mAh", "Powerbank z szybkim ładowaniem", "159.00", 25),
            ("Torba na laptopa", "Torba materiałowa na laptop 15 cali", "119.00", 30),
            ("Kamera internetowa", "Kamera Full HD do spotkań online", "179.90", 20),
            ("Podkładka pod mysz", "Duża podkładka materiałowa", "39.99", 80),
            ("Router Wi-Fi", "Dwupasmowy router domowy", "249.00", 16),
            ("Dysk SSD 1 TB", "Dysk SSD SATA 1 TB", "399.00", 14),
        ]
        for nazwa, opis, cena, stan in produkty_data:
            Produkt.objects.get_or_create(
                nazwa_produktu=nazwa,
                defaults={
                    "opis": opis,
                    "cena_produktu": Decimal(cena),
                    "stan_magazynowy": stan,
                },
            )

        self.stdout.write("Tworzenie zamówień...")

        # WAŻNE: zamówień nie da się sensownie deduplikować przez get_or_create
        # (każde nowe ma inną datę, klient mógłby zamówić to samo dwa razy).
        # Dlatego sprawdzamy z góry, czy zamówienia w bazie już są.
        # Jeśli tak – pomijamy ten krok, żeby kolejne uruchomienia komendy nie tworzyły duplikatów.
        if Zamowienie.objects.exists():
            self.stdout.write(self.style.WARNING(
                "  Pomijam – w bazie są już jakieś zamówienia. "
                "Jeśli chcesz wczytać świeży zestaw, najpierw skasuj zamówienia "
                "(np. w panelu admina) albo wyczyść bazę."
            ))
            self.stdout.write(self.style.SUCCESS("Dane demonstracyjne załadowane."))
            return

        def klient_po_email(email):
            return Klient.objects.get(uzytkownik__email=email)

        def produkt_po_nazwie(nazwa):
            return Produkt.objects.get(nazwa_produktu=nazwa)

        zamowienia_data = [
            # (email, status, adres, [(nazwa_produktu, ilosc, cena_jedn)])
            ("jan.kowalski@example.com", "zrealizowane", "ul. Kwiatowa 12, 00-001 Warszawa",
             [("Klawiatura mechaniczna", 1, "249.99"),
              ("Mysz bezprzewodowa", 1, "89.90"),
              ("Podkładka pod mysz", 1, "39.99")]),
            ("jan.kowalski@example.com", "wyslane", "ul. Kwiatowa 12, 00-001 Warszawa",
             [("Słuchawki Bluetooth", 1, "199.99"),
              ("Kabel USB-C", 2, "29.99"),
              ("Powerbank 20000 mAh", 1, "159.00")]),
            ("anna.nowak@example.com", "zrealizowane", "ul. Leśna 5, 30-002 Kraków",
             [("Monitor 27 cali", 1, "749.00"),
              ("Kamera internetowa", 1, "179.90")]),
            ("anna.nowak@example.com", "oplacone", "ul. Leśna 5, 30-002 Kraków",
             [("Dysk SSD 1 TB", 1, "399.00"),
              ("Kabel USB-C", 3, "29.99")]),
            ("piotr.wisniewski@example.com", "anulowane", "ul. Słoneczna 8, 60-003 Poznań",
             [("Laptop 15 cali", 1, "3299.00")]),
            ("piotr.wisniewski@example.com", "nowe", "ul. Słoneczna 8, 60-003 Poznań",
             [("Torba na laptopa", 1, "119.00"),
              ("Podkładka pod mysz", 2, "39.99"),
              ("Mysz bezprzewodowa", 1, "89.90")]),
            ("maria.zielinska@example.com", "oplacone", "ul. Ogrodowa 21, 80-004 Gdańsk",
             [("Router Wi-Fi", 1, "249.00"),
              ("Kabel USB-C", 2, "29.99")]),
            ("tomasz.wojcik@example.com", "wyslane", "ul. Lipowa 3, 50-005 Wrocław",
             [("Klawiatura mechaniczna", 1, "249.99"),
              ("Słuchawki Bluetooth", 1, "199.99"),
              ("Podkładka pod mysz", 1, "39.99")]),
            ("tomasz.wojcik@example.com", "nowe", "ul. Lipowa 3, 50-005 Wrocław",
             [("Powerbank 20000 mAh", 1, "159.00"),
              ("Kabel USB-C", 1, "29.99")]),
        ]

        for email, status, adres, pozycje in zamowienia_data:
            klient = klient_po_email(email)
            zamowienie = Zamowienie.objects.create(
                klient=klient, status=status, adres_dostawy=adres, wartosc_zamowienia=0,
            )
            wartosc = Decimal("0")
            for nazwa, ilosc, cena in pozycje:
                p = produkt_po_nazwie(nazwa)
                cena_dec = Decimal(cena)
                PozycjaZamowienia.objects.create(
                    zamowienie=zamowienie, produkt=p, ilosc=ilosc, cena_jednostkowa=cena_dec,
                )
                wartosc += cena_dec * ilosc
            zamowienie.wartosc_zamowienia = wartosc
            zamowienie.save()

        self.stdout.write(self.style.SUCCESS("Dane demonstracyjne załadowane."))