# System Domu Aukcyjnego (Auction House Web App)

Projekt internetowego systemu aukcyjnego zrealizowany w frameworku Django. Aplikacja umożliwia użytkownikom przeglądanie, wystawianie oraz licytowanie przedmiotów w czasie rzeczywistym, a także automatyzuje proces generowania rachunków i obsługi płatności przez panel administracyjny (pracowników).

---

## Funkcjonalności

### Panel Klienta
* **Rejestracja i Profile:** Formularz rejestracyjny tworzący konto użytkownika wraz z adresem zamieszkania, przypisaniem roli oraz profilem.
* **Przeglądanie i Licytacja:** Dostęp do listy aktywnych aukcji oraz widoku szczegółowego. System automatycznie waliduje oferty (oferta musi być wyższa od ceny wywoławczej oraz od aktualnie najwyższej oferty).
* **Zarządzanie:** Dedykowane widoki dla ofert użytkownika, licytowanych przedmiotów oraz historii własnych aukcji.
* **Płatności:** Możliwość opłacenia wygranych aukcji poprzez wybór metody płatności (Karta/Gotówka).

### Panel Pracownika (Staff)
* **Zamykanie aukcji:** Wykaz aukcji, których termin zakończenia już minął.
* **Wystawianie rachunków:** Automatyczne generowanie faktury/płatności dla użytkownika, który złożył najwyższą ofertę w momencie zakończenia aukcji.
* **Zatwierdzanie płatności:** Przegląd oczekujących wpłat i funkcja ich potwierdzania, połączona z automatyczną wysyłką mailową z potwierdzeniem.

---

## Technologie

* **Backend:** Python 3.x, Django Framework
* **Baza danych:** SQLite (domyślna)
* **Walidacja i Logika:** Transakcje atomowe (`@transaction.atomic`), niestandardowe walidacje modeli (`clean()`)
* **Testy:** Django TestCase, Coverage (analiza pokrycia kodu)

---

Struktura Projektu
```
📂 dom_aukcyjny/                  # Główny folder projektu (repozytorium)
├── 📂 serwis_aukcyjny/          # Folder konfiguracyjny projektu Django
│   ├── 📄 __init__.py
│   ├── 📄 asgi.py
│   ├── 📄 settings.py           # Ustawienia projektu
│   ├── 📄 urls.py               # Główny routing projektu
│   └── 📄 wsgi.py
├── 📂 serwis/                   # Główny folder Twojej aplikacji aukcyjnej
│   ├── 📂 migrations/           # Migracje bazy danych
│   ├── 📂 templates/            # Szablony HTML
│   │   ├── 📂 registration/     # Szablony logowania / rejestracji (np. sing_up.html)
│   │   └── 📂 serwis/           # Szablony widoków aukcji (np. start_page.html, auction_detail.html)
│   ├── 📄 __init__.py
│   ├── 📄 admin.py              # Konfiguracja panelu admina
│   ├── 📄 apps.py
│   ├── 📄 emails.py             # Obsługa wysyłki maili (potwierdzenia płatności)
│   ├── 📄 forms.py              # Formularze (rejestracja, nowa oferta, dodanie aukcji)
│   ├── 📄 models.py             # Modele bazy danych (Aukcja, Oferta, Platnosc itp.)
│   ├── 📄 tests.py              # Testy jednostkowe i integracyjne
│   └── 📄 views.py              # Logika widoków aplikacji
├── 📂 media/                    # Pliki przesłane przez użytkowników (np. zdjęcia produktów)
│   └── 📂 auction_image/
├── 📄 .coveragerc               # Konfiguracja wykluczeń dla narzędzia coverage
├── 📄 db.sqlite3                # Lokalna baza danych SQLite
├── 📄 manage.py                 # Skrypt zarządzający projektami Django
├── 📄 README.md                 # Dokumentacja projektu
└── 📄 requirements.txt          # Lista zależności (Django, coverage itp.)
```
---

## Instalacja i Uruchomienie

1. Zainstaluj wymagane pakiety
  ```pip install -r requirements.txt``1
2. Wykonaj migracje bazy danych
   ```python manage.py makemigrations```
   ```python manage.py migrate```
3. Utwórz konto administratora
   ```python manage.py createsuperuser```
4. Uruchom serwer deweloperski
   ```python manage.py runserver```
5. Jeżeli wszytko sie powiedzie odpal w przeglądarce
   ```http://127.0.0.1:8000/```
---

## Projekt zawiera wbudowany zestaw testów jednostkowych i integracyjnych sprawdzających kluczową logikę biznesową (generowanie slugów, walidację stawek, automatyczne wystawianie rachunków oraz zabezpieczenia widoków).
1. Uruchomienie testów:
```python manage.py test```

Sprawdzenie pokrycia kodu (Coverage):
```
coverage run --source='.' manage.py test
coverage report
```
---
