from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction # Dodany import transakcji
from serwis.models import (
    ProfilUzytkownika, Adres, Uzytkownik, Kategoria, Aukcja, Oferta, Platnosc
)
from datetime import timedelta, date
from django.utils import timezone

class Command(BaseCommand):
    help = "Ładuje logiczne dane demonstracyjne dla portalu aukcyjnego"

    def handle(self, *args, **options):
        # 1. Zabezpieczenie przed dublowaniem danych
        if Aukcja.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Pomijam – w bazie są już dane. "
                "Wpisz w konsoli 'python manage.py flush', aby wyczyścić bazę przed wgraniem demo."
            ))
            return

        # 2. Blok transakcji - chroni przed zapisaniem "połowy" danych w razie błędu
        with transaction.atomic():
            self.stdout.write("1. Tworzenie użytkowników i ich adresów...")
            
            uzytkownicy_data = [
                # username, email, imie, nazwisko, tel, rola, kraj, miasto, ulica, kod, bud, lok
                ("jan.kowalski", "jan@example.com", "Jan", "Kowalski", "500100200", 
                 "Klient", "Polska", "Warszawa", "Kwiatowa", "00-001", "12", None),
                
                ("anna.nowak", "anna@example.com", "Anna", "Nowak", "501200300", 
                 "Klient", "Polska", "Kraków", "Leśna", "30-002", "5", "14"),
                
                ("piotr.wisniewski", "piotr@example.com", "Piotr", "Wiśniewski", "502300400", 
                 "Klient", "Polska", "Poznań", "Słoneczna", "60-003", "8", None),
                
                ("admin_sklepu", "admin@sklep.pl", "Ewa", "Kaczmarek", "500000000", 
                 "Pracownik", "Polska", "Wrocław", "Biurowa", "50-000", "1", "1"),
            ]

            for username, email, imie, nazwisko, tel, rola, kraj, miasto, ulica, kod, budynek, lokal in uzytkownicy_data:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"email": email, "first_name": imie, "last_name": nazwisko},
                )
                if created:
                    user.set_password("Demo1234!") # Wspólne hasło
                    if rola == "Pracownik":
                        user.is_staff = True
                        user.is_superuser = True # Pełen dostęp dla admina
                    user.save()

                # POPRAWKA: uzytkownik=user (zgodnie z Twoim modes.py)
                ProfilUzytkownika.objects.get_or_create(uzytkownik=user, defaults={"rola": rola})

                adres, _ = Adres.objects.get_or_create(
                    kraj=kraj, miasto=miasto, ulica=ulica, kod_pocztowy=kod, 
                    numer_budynku=budynek, numer_lokalu=lokal
                )

                Uzytkownik.objects.get_or_create(
                    uzytkownik=user,
                    defaults={"adres": adres, "telefon": tel, "data_rejestracji": date.today()}
                )

            self.stdout.write("2. Tworzenie kategorii...")
            kategorie_nazwy = ["Elektronika", "Motoryzacja", "Dom i Ogród", "Kolekcje", "Moda", "Sport"]
            for nazwa in kategorie_nazwy:
                Kategoria.objects.get_or_create(nazwa=nazwa)

            self.stdout.write("3. Tworzenie logicznych aukcji...")
            
            def get_uzytkownik_model(username):
                return Uzytkownik.objects.get(uzytkownik__username=username)

            def get_user_model(username):
                return User.objects.get(username=username)

            def get_kategoria(nazwa):
                return Kategoria.objects.get(nazwa=nazwa)

            za_tydzien = date.today() + timedelta(days=7)
            wczoraj = date.today() - timedelta(days=1)

            aukcje_data = [
                # Jan sprzedaje:
                ("jan.kowalski", "Elektronika", "Laptop gamingowy 15 cali", 2500.0, za_tydzien, "Aktywny"),
                ("jan.kowalski", "Motoryzacja", "Opony letnie 16", 400.0, za_tydzien, "Aktywny"),
                
                # Anna sprzedaje:
                ("anna.nowak", "Dom i Ogród", "Zestaw mebli ogrodowych", 800.0, wczoraj, "Zakonczone"),
                ("anna.nowak", "Moda", "Kurtka skórzana męska L", 150.0, za_tydzien, "Aktywny"),
                
                # Piotr sprzedaje:
                ("piotr.wisniewski", "Kolekcje", "Złota moneta 1 uncja", 8000.0, za_tydzien, "Aktywny"),
                ("piotr.wisniewski", "Sport", "Rower górski KROSS", 1200.0, wczoraj, "Zakonczone"),
            ]

            for sprzedajacy_username, kat_nazwa, nazwa, cena, data_zak, status in aukcje_data:
                Aukcja.objects.get_or_create(
                    nazwa_produktu=nazwa,
                    defaults={
                        "sprzedajacy": get_uzytkownik_model(sprzedajacy_username),
                        "kategoria": get_kategoria(kat_nazwa),
                        "cena_wywolawcza": cena,
                        "data_zakonczenia": data_zak,
                        "status": status,
                        "opis": f"Opis wygenerowany dla: {nazwa}. Świetny produkt!",
                    }
                )

            self.stdout.write("4. Symulacja licytacji (Oferty rosnące)...")
            
            oferty_data = [
                # Aukcja Jana -> Licytuje Anna i Piotr
                ("Laptop gamingowy 15 cali", "anna.nowak", 2600.0),
                ("Laptop gamingowy 15 cali", "piotr.wisniewski", 2750.0),

                # Aukcja Jana -> Licytuje tylko Piotr
                ("Opony letnie 16", "piotr.wisniewski", 450.0),

                # Aukcja Anny (ZAKOŃCZONA) -> Licytuje Jan i Piotr, Jan wygrywa
                ("Zestaw mebli ogrodowych", "jan.kowalski", 850.0),
                ("Zestaw mebli ogrodowych", "piotr.wisniewski", 900.0),
                ("Zestaw mebli ogrodowych", "jan.kowalski", 950.0), 

                # Aukcja Piotra -> Licytuje Jan i Anna
                ("Złota moneta 1 uncja", "jan.kowalski", 8100.0),
                ("Złota moneta 1 uncja", "anna.nowak", 8200.0),

                # Aukcja Piotra (ZAKOŃCZONA) -> Licytuje Anna
                ("Rower górski KROSS", "anna.nowak", 1300.0), 
            ]

            for aukcja_nazwa, kupujacy_username, kwota in oferty_data:
                aukcja = Aukcja.objects.get(nazwa_produktu=aukcja_nazwa)
                kupujacy_user = get_user_model(kupujacy_username) 
                
                # Tworzymy ofertę używając obiektu, by zadziałał clean()
                oferta = Oferta(aukcja=aukcja, kupujacy=kupujacy_user, oferowana_cena=kwota)
                oferta.clean() # Uruchamia Twoją walidację ceny!
                oferta.save()

            self.stdout.write("5. Generowanie płatności dla zakończonych aukcji...")

            platnosci_data = [
                # Zestaw mebli (wygrany przez Jana za 950 u Anny)
                ("Zestaw mebli ogrodowych", "jan.kowalski", "Zaplacone", 950.0, "Karta"),
                
                # Rower (wygrany przez Annę za 1300 u Piotra)
                ("Rower górski KROSS", "anna.nowak", "Nie Zaplacone", 1300.0, "Gotowka"),
            ]

            for aukcja_nazwa, platnik_username, status, kwota, metoda in platnosci_data:
                aukcja = Aukcja.objects.get(nazwa_produktu=aukcja_nazwa)
                platnik = get_uzytkownik_model(platnik_username)
                
                Platnosc.objects.create(
                    aukcja=aukcja,
                    platnik=platnik,
                    status_platnosci=status,
                    cena_koncowa=kwota,
                    metoda_platnosc=metoda
                )

            self.stdout.write(self.style.SUCCESS("Gotowe! Dane są spójne i w 100% gotowe do testowania widoków."))