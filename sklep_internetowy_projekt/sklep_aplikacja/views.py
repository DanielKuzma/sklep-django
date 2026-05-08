from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Produkt, Zamowienie

# Create your views here.
def strona_glowna(request):
    kontekst = {
        "nazwa_sklepu": "Mój Sklep",
        "rok": 2026,
    }
    return render(request, "sklep_aplikacja/strona_glowna.html", kontekst)



def lista_produktow(request):
    produkty = Produkt.objects.filter(czy_aktywny=True).order_by("nazwa_produktu")

    # 12 oznacza liczbę produktów na jednej stronie.
    paginator = Paginator(produkty, 12)
    numer_strony = request.GET.get("page")

    # get_page() jest przyjazne dla początkujących: obsłuży brak strony i błędny numer.
    page_obj = paginator.get_page(numer_strony)

    return render(request, "sklep_aplikacja/lista_produktow.html", {
        "page_obj": page_obj,
    })

def szczegoly_produktu(request, id_produktu):
    produkt = get_object_or_404(Produkt, id=id_produktu, czy_aktywny=True)
    return render(request, "sklep_aplikacja/szczegoly_produktu.html", {
        "produkt": produkt,
    })

def test_dane(request):
    liczba_produktow = Produkt.objects.count()
    liczba_zamowien = Zamowienie.objects.count()
    aktywne = Produkt.objects.filter(czy_aktywny=True).count()
    return HttpResponse(
        f"Produkty: {liczba_produktow} (aktywne: {aktywne}), "
        f"Zamówienia: {liczba_zamowien}"
    )