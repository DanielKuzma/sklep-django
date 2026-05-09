import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def wyslij_potwierdzenie_zamowienia(zamowienie):
    """Wysyła klientowi potwierdzenie + pracownikom powiadomienie. Best-effort."""
    klient_email = zamowienie.klient.uzytkownik.email
    if not klient_email:
        logger.warning("Zamówienie #%s – klient bez e-maila, pomijam wysyłkę.", zamowienie.pk)
        return

    kontekst = {
        "zamowienie": zamowienie,
        "pozycje": zamowienie.pozycje.select_related("produkt"),
    }
    tresc_klient = render_to_string("sklep_aplikacja/emails/potwierdzenie_klient.txt", kontekst)
    tresc_pracownik = render_to_string("sklep_aplikacja/emails/powiadomienie_pracownik.txt", kontekst)

    try:
        # 1) Klient: potwierdzenie.
        send_mail(
            subject=f"Potwierdzenie zamówienia #{zamowienie.pk}",
            message=tresc_klient,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[klient_email],
            fail_silently=False,
        )
        # 2) Pracownik(-cy): powiadomienie. Lista z settings, żeby nie mieszać w kodzie.
        if settings.EMAIL_PRACOWNIKOW:
            send_mail(
                subject=f"Nowe zamówienie #{zamowienie.pk}",
                message=tresc_pracownik,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.EMAIL_PRACOWNIKOW,
                fail_silently=False,
            )
    except Exception as e:
        # Nie podnosimy wyjątku – zamówienie już istnieje, e-mail to dodatek.
        logger.exception("Nie udało się wysłać e-maila dla zamówienia #%s: %s", zamowienie.pk, e)