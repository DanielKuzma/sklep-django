import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def wyslij_potwierdzenie_platnosci(platnosc):  
    klient_email = platnosc.platnik.uzytkownik.email
    
    if not klient_email:
        logger.warning("Płatność #%s – klient bez e-maila, pomijam wysyłkę.", platnosc.pk)
        return

    kontekst = {
        "platnosc": platnosc,
        "aukcja": platnosc.aukcja,
    }
    
    tresc_klient = render_to_string("emails/potwierdzenie_wplaty_klient.txt", kontekst)

    try:
        send_mail(
            subject=f"Potwierdzenie zapłaty za aukcję: {platnosc.aukcja.nazwa_produktu}",
            message=tresc_klient,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[klient_email],
            fail_silently=False,
        )
        
    except Exception as e:
        logger.exception("Nie udało się wysłać e-maila dla płatności #%s: %s", platnosc.pk, e)