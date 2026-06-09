from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from serwis.models import (
    ProfilUzytkownika, Adres, Uzytkownik, Kategoria, Aukcja, Oferta, Platnosc
)
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = "Ładuje logiczne dane demonstracyjne dla portalu aukcyjnego"

    def handle(self, *args, **options):
        # 1. Zabezpieczenie przed dublowaniem danych
        if Aukcja.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Pomijam – w bazie są już dane. "
                "Wpisz w konsoli 'python manage.py flush', aby wyczyścić bazę."
            ))
            return

        with transaction.atomic():
            self.stdout.write("1. Tworzenie użytkowników i ich adresów...")
            
            teraz = timezone.now()
            
            uzytkownicy_data = [
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
                    user.set_password("Demo1234!")
                    if rola == "Pracownik":
                        user.is_staff = True
                        user.is_superuser = True
                    user.save()

                ProfilUzytkownika.objects.get_or_create(uzytkownik=user, defaults={"rola": rola})

                adres, _ = Adres.objects.get_or_create(
                    kraj=kraj, miasto=miasto, ulica=ulica, kod_pocztowy=kod, 
                    numer_budynku=budynek, numer_lokalu=lokal
                )

                Uzytkownik.objects.get_or_create(
                    uzytkownik=user,
                    defaults={"adres": adres, "telefon": tel, "data_rejestracji": teraz.date()}
                )

            self.stdout.write("2. Tworzenie kategorii...")
            kategorie_nazwy = ["Elektronika", "Motoryzacja", "Dom i Ogród", "Kolekcje", "Moda", "Sport"]
            for nazwa in kategorie_nazwy:
                Kategoria.objects.get_or_create(nazwa=nazwa)

            self.stdout.write("3. Tworzenie logicznych aukcji z dopasowanymi obrazami...")
            
            def get_uzytkownik_model(username):
                return Uzytkownik.objects.get(uzytkownik__username=username)

            def get_user_model(username):
                return User.objects.get(username=username)

            def get_kategoria(nazwa):
                return Kategoria.objects.get(nazwa=nazwa)

            # --- DYNAMIZACJA DAT ---
            za_tydzien = teraz + timedelta(days=7)
            jutro = teraz + timedelta(days=1)
            wczoraj = teraz - timedelta(days=1)
            dawno = teraz - timedelta(days=30)

            # Dodaliśmy siódmy parametr: względną ścieżkę pliku wewnątrz katalogu media/
            aukcje_data = [
                # Aktywne (kończą się w przyszłości)
                ("jan.kowalski", "Elektronika", "Laptop gamingowy 15 cali", 2500.0, za_tydzien, "Aktywny", "auction_image/laptop.jpg"),
                ("jan.kowalski", "Motoryzacja", "Opony letnie 16", 400.0, jutro, "Aktywny", "auction_image/opony.jpg"),
                ("anna.nowak", "Moda", "Kurtka skórzana męska L", 150.0, za_tydzien, "Aktywny", "auction_image/kurtka.jpg"),
                ("piotr.wisniewski", "Kolekcje", "Złota moneta 1 uncja", 8000.0, za_tydzien, "Aktywny", "auction_image/moenta.jpg"), # Uwzględniono 'moenta.jpg' z drzewa plików
                
                # Zakończone (data zakończenia w przeszłości)
                ("anna.nowak", "Dom i Ogród", "Zestaw mebli ogrodowych", 800.0, wczoraj, "Zakonczone", "auction_image/meble.jpg"),
                ("piotr.wisniewski", "Sport", "Rower górski KROSS", 1200.0, dawno, "Zakonczone", "auction_image/rower.jpg"),
            ]

            for sprzedajacy_username, kat_nazwa, nazwa, cena, data_zak, status, foto in aukcje_data:
                Aukcja.objects.get_or_create(
                    nazwa_produktu=nazwa,
                    defaults={
                        "sprzedajacy": get_uzytkownik_model(sprzedajacy_username),
                        "kategoria": get_kategoria(kat_nazwa),
                        "cena_wywolawcza": cena,
                        "data_zakonczenia": data_zak,
                        "status": status,
                        "opis": f"Opis wygenerowany dla: {nazwa}. Świetny produkt!",
                        # UWAGA: Jeżeli Twoje pole w modelu Aukcja nazywa się inaczej niż "zdjecie" (np. "obrazek", "miniaturka"), zmień poniższy klucz:
                        "zdjecie": foto, 
                    }
                )

            self.stdout.write("4. Symulacja licytacji...")
            
            oferty_data = [
                ("Laptop gamingowy 15 cali", "anna.nowak", 2600.0),
                ("Laptop gamingowy 15 cali", "piotr.wisniewski", 2750.0),
                ("Opony letnie 16", "piotr.wisniewski", 450.0),
                ("Zestaw mebli ogrodowych", "jan.kowalski", 850.0),
                ("Zestaw mebli ogrodowych", "piotr.wisniewski", 900.0),
                ("Zestaw mebli ogrodowych", "jan.kowalski", 950.0), 
                ("Złota moneta 1 uncja", "jan.kowalski", 8100.0),
                ("Złota moneta 1 uncja", "anna.nowak", 8200.0),
                ("Rower górski KROSS", "anna.nowak", 1300.0), 
            ]

            for aukcja_nazwa, kupujacy_username, kwota in oferty_data:
                aukcja = Aukcja.objects.get(nazwa_produktu=aukcja_nazwa)
                kupujacy_user = get_user_model(kupujacy_username) 
                oferta = Oferta(aukcja=aukcja, kupujacy=kupujacy_user, oferowana_cena=kwota)
                oferta.clean() 
                oferta.save()

            self.stdout.write("5. Generowanie płatności...")

            platnosci_data = [
                ("Zestaw mebli ogrodowych", "jan.kowalski", "Zaplacone", 950.0, "Karta"),
                ("Rower górski KROSS", "anna.nowak", "Nie Zaplacone", 1300.0, "Gotowka"),
            ]

            for aukcja_nazwa, platnik_username, status, kwota, metoda in platnosci_data:
                aukcja = Aukcja.objects.get(nazwa_produktu=aukcja_nazwa)
                platnik = get_uzytkownik_model(platnik_username)
                Platnosc.objects.create(
                    aukcja=aukcja, platnik=platnik, status_platnosci=status,
                    cena_koncowa=kwota, metoda_platnosc=metoda
                )

            self.stdout.write(self.style.SUCCESS("Gotowe! Daty oraz ścieżki multimediów zostały pomyślnie zsynchronizowane."))