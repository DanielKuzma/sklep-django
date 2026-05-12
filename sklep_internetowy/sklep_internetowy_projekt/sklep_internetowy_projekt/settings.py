"""
Django settings for sklep_internetowy_projekt project.
"""
import sys
from pathlib import Path
from decouple import config, Csv
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# GŁÓWNE USTAWIENIA (Localhost vs Produkcja)
# ==========================================
SECRET_KEY = config("DJANGO_SECRET_KEY")

# Pamiętaj, aby w pliku .env ustawić DJANGO_DEBUG=True podczas pracy lokalnej!
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# ==========================================
# APLIKACJE I MIDDLEWARE
# ==========================================
INSTALLED_APPS = [
    "sklep_aplikacja",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Gotowe na serwowanie statyki na produkcji
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "sklep_internetowy_projekt.urls"
WSGI_APPLICATION = "sklep_internetowy_projekt.wsgi.application"

# ==========================================
# SZABLONY
# ==========================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ==========================================
# BAZA DANYCH (Główna: PostgreSQL)
# ==========================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Podczas uruchamiania testów, Django użyje lekkiej bazy SQLite
if "test" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }

# ==========================================
# AUTENTYKACJA I BEZPIECZEŃSTWO HASEŁ
# ==========================================
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Ustawienia logowania (Axes)
AXES_FAILURE_LIMIT = 5              # 5 nieudanych prób...
AXES_COOLOFF_TIME = 1               # ...blokuje na 1 godzinę
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]  # blokujemy IP+login
AXES_RESET_ON_SUCCESS = True        # udane logowanie kasuje licznik

# Przekierowania
LOGIN_REDIRECT_URL = "strona_glowna"
LOGOUT_REDIRECT_URL = "strona_glowna"
LOGIN_URL = "login"

# Sesje
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 tygodnie

# ==========================================
# INTERNACJONALIZACJA
# ==========================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==========================================
# PLIKI STATYCZNE I MEDIA
# ==========================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==========================================
# EMAILE I WIADOMOŚCI
# ==========================================
MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "sklep@example.com"
EMAIL_PRACOWNIKOW = ["zamowienia@example.com"]

# ==========================================
# USTAWIENIA PRODUKCYJNE (Aktywne gdy DEBUG = False)
# ==========================================
if not DEBUG:
    # Wymuszenie HTTPS i nagłówki bezpieczeństwa
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # Zabezpieczenie ciasteczek sesji i CSRF
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = "Lax"