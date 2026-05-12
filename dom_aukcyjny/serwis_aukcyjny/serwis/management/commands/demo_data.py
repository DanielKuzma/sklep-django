from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# UWAGA: Zamień 'serwis' na nazwę Twojej aplikacji, jeśli jest inna!
from serwis.models import ProfilUzytkowniak, Adres, Uzytkownik, Kategoria, Aukcja, Oferta, Platnosc 

class Command(BaseCommand):
    help = "Ładuje sensowne, rozbudowane dane testowe do serwisu aukcyjnego"

    def handle(self, *args, **options):
        self.stdout.write("Czyszczenie starych danych (jeśli jakieś zostały)...")
        Oferta.objects.all().delete()
        Platnosc.objects.all().delete()
        Aukcja.objects.all().delete()
        Kategoria.objects.all().delete()
        Uzytkownik.objects.all().delete()
        Adres.objects.all().delete()
        ProfilUzytkowniak.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete() # Zostawiamy tylko admina

        self.stdout.write("1. Tworzenie użytkowników i adresów...")
        # Hasło dla wszystkich to: testowe123
        dane_ludzi = [
            ("jan_sprzedawca", "jan@aukcje.pl", "Jan", "Kowalski", "111222333", "Warszawa"),
            ("ania_biznes", "ania@aukcje.pl", "Anna", "Nowak", "444555666", "Kraków"),
            ("tomek_kupiec", "tomek@aukcje.pl", "Tomasz", "Wójcik", "777888999", "Poznań"),
            ("kasia_lowca", "kasia@aukcje.pl", "Katarzyna", "Lis", "123123123", "Gdańsk"),
            ("piotrek_licytator", "piotr@aukcje.pl", "Piotr", "Zając", "321321321", "Wrocław"),
        ]

        uzytkownicy = {}
        for username, email, imie, nazwisko, tel, miasto in dane_ludzi:
            # Tworzymy systemowego usera
            user = User.objects.create_user(username=username, email=email, password="testowe123", first_name=imie, last_name=nazwisko)
            
            # Tworzymy profil
            rola = "Pracownik" if "sprzedawca" in username else "Klient"
            ProfilUzytkowniak.objects.create(uzytkownik=user, rola=rola)
            
            # Tworzymy adres
            adres = Adres.objects.create(ulica="Główna", numer_budynku="1", kod_pocztowy="00-000", miasto=miasto, kraj="Polska")
            
            # Tworzymy profil rozszerzony (Twój model Uzytkownik)
            uzytkownicy[username] = Uzytkownik.objects.create(uzytkownik=user, adres=adres, nazwa_uzytkownika=username, telefon=tel)

        self.stdout.write("2. Tworzenie kategorii...")
        kat_elektronika = Kategoria.objects.create(nazwa="Elektronika")
        kat_motoryzacja = Kategoria.objects.create(nazwa="Motoryzacja")
        kat_dom = Kategoria.objects.create(nazwa="Dom i Ogród")
        kat_sport = Kategoria.objects.create(nazwa="Sport i Rekreacja")

        self.stdout.write("3. Tworzenie aukcji...")
        dzisiaj = timezone.now().date()
        
        aukcje = {
            # AKTYWNE AUKCJE
            "laptop": Aukcja.objects.create(
                sprzedajacy=uzytkownicy["jan_sprzedawca"], kategoria=kat_elektronika,
                nazwa_produktu="MacBook Pro M1 (Stan Idealny)", cena_wywolawcza=3000.0,
                data_zakonczenia=dzisiaj + timedelta(days=5), opis="Świetny laptop do pracy.", status="Aktywny"
            ),
            "rower": Aukcja.objects.create(
                sprzedajacy=uzytkownicy["ania_biznes"], kategoria=kat_sport,
                nazwa_produktu="Rower Górski Kross", cena_wywolawcza=800.0,
                data_zakonczenia=dzisiaj + timedelta(days=2), opis="Rower używany, gotowy do jazdy.", status="Aktywny"
            ),
            "kosiarka": Aukcja.objects.create(
                sprzedajacy=uzytkownicy["ania_biznes"], kategoria=kat_dom,
                nazwa_produktu="Kosiarka Spalinowa Nowa", cena_wywolawcza=450.0,
                data_zakonczenia=dzisiaj + timedelta(days=7), opis="Oryginalnie zapakowana.", status="Aktywny"
            ),
            # ZAKOŃCZONE AUKCJE
            "opony": Aukcja.objects.create(
                sprzedajacy=uzytkownicy["jan_sprzedawca"], kategoria=kat_motoryzacja,
                nazwa_produktu="Komplet opon zimowych 16'", cena_wywolawcza=500.0,
                data_zakonczenia=dzisiaj - timedelta(days=3), opis="Bieżnik 6mm.", status="Zakonczone"
            ),
            "konsola": Aukcja.objects.create(
                sprzedajacy=uzytkownicy["jan_sprzedawca"], kategoria=kat_elektronika,
                nazwa_produktu="PlayStation 5 z padem", cena_wywolawcza=1800.0,
                data_zakonczenia=dzisiaj - timedelta(days=1), opis="Mało używana.", status="Zakonczone"
            ),
        }

        # Generujemy slug dla każdej aukcji
        for aukcja in aukcje.values():
            aukcja.save()

        self.stdout.write("4. Generowanie historii ofert (wojny licytacyjne)...")
        # MacBook (Aktywna) - zacięta walka Tomka i Kasi
        Oferta.objects.create(aukcja=aukcje["laptop"], kupujacy=uzytkownicy["tomek_kupiec"], oferowana_cena=3100.0)
        Oferta.objects.create(aukcja=aukcje["laptop"], kupujacy=uzytkownicy["kasia_lowca"], oferowana_cena=3300.0)
        Oferta.objects.create(aukcja=aukcje["laptop"], kupujacy=uzytkownicy["tomek_kupiec"], oferowana_cena=3550.0)

        # Rower (Aktywna) - jedna oferta
        Oferta.objects.create(aukcja=aukcje["rower"], kupujacy=uzytkownicy["piotrek_licytator"], oferowana_cena=850.0)

        # Kosiarka - BRAK OFERT (żebyś miał jak testować puste aukcje)

        # Opony (Zakończona) - wygrał Piotrek
        Oferta.objects.create(aukcja=aukcje["opony"], kupujacy=uzytkownicy["tomek_kupiec"], oferowana_cena=550.0)
        Oferta.objects.create(aukcja=aukcje["opony"], kupujacy=uzytkownicy["piotrek_licytator"], oferowana_cena=600.0)

        # Konsola (Zakończona) - wygrała Kasia
        Oferta.objects.create(aukcja=aukcje["konsola"], kupujacy=uzytkownicy["kasia_lowca"], oferowana_cena=1950.0)

        self.stdout.write("5. Księgowanie płatności dla zakończonych aukcji...")
        # Piotrek nie zapłacił jeszcze za opony
        Platnosc.objects.create(
            aukcja=aukcje["opony"], platnik=uzytkownicy["piotrek_licytator"], 
            status_platnosci="Nie Zaplacone", cena_koncowa=600.0, metoda_platnosc="Gotowka"
        )
        
        # Kasia zapłaciła za konsolę
        Platnosc.objects.create(
            aukcja=aukcje["konsola"], platnik=uzytkownicy["kasia_lowca"], 
            status_platnosci="Zaplacone", cena_koncowa=1950.0, metoda_platnosc="Karta"
        )

        self.stdout.write(self.style.SUCCESS("Gotowe! Wgrano doskonały zestaw danych do pracy i testów."))
        self.stdout.write("Loginy: jan_sprzedawca, ania_biznes, tomek_kupiec, kasia_lowca, piotrek_licytator")
        self.stdout.write("Hasło dla wszystkich to: testowe123")