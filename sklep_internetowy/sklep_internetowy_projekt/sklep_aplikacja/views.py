from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Produkt, Zamowienie, PozycjaZamowienia, Klient, ProfilUzytkownika
from .forms import ZmianaStatusuForm, RejestracjaKlientaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST
from .koszyk import Koszyk
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from .emails import wyslij_potwierdzenie_zamowienia
from django_ratelimit.decorators import ratelimit


# Create your views here.
def jest_pracownikiem(user):
    # Najpierw sprawdzamy, czy ktoś w ogóle jest zalogowany.
    if not user.is_authenticated:
        return False
    # Superużytkownik i administrator mają is_staff=True.
    if user.is_staff:
        return True
    # Zwykły pracownik ma rolę "pracownik" w ProfilUzytkownika.
    profil = getattr(user, "profiluzytkownika", None)
    return profil is not None and profil.rola == "pracownik"

def strona_glowna(request):
    kontekst = {
        "nazwa_sklepu": "Mój Sklep",
        "rok": 2026,
    }
    return render(request, "sklep_aplikacja/strona_glowna.html", kontekst)

@ratelimit(key="ip", rate="60/m", method="GET", block=True)
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

def szczegoly_produktu(request, slug):
    produkt = get_object_or_404(Produkt, slug=slug, czy_aktywny=True)
    return render(request, "sklep_aplikacja/szczegoly_produktu.html", {"produkt": produkt})

def test_dane(request):
    liczba_produktow = Produkt.objects.count()
    liczba_zamowien = Zamowienie.objects.count()
    aktywne = Produkt.objects.filter(czy_aktywny=True).count()
    return HttpResponse(
        f"Produkty: {liczba_produktow} (aktywne: {aktywne}), "
        f"Zamówienia: {liczba_zamowien}"
    )

@login_required
@user_passes_test(jest_pracownikiem)
def zmien_status_zamowienia(request, id_zamowienia):
    # Jeśli zamówienie nie istnieje, Django zwróci stronę 404.
    zamowienie = get_object_or_404(Zamowienie, pk=id_zamowienia)

    if request.method == "POST":
        # request.POST zawiera dane wysłane formularzem.
        # instance=zamowienie oznacza edycję istniejącego obiektu, a nie tworzenie nowego.
        formularz = ZmianaStatusuForm(request.POST, instance=zamowienie)
        if formularz.is_valid():
            formularz.save()
            # Przekierowanie wracające pracownika na listę zamówień,
            # którą zbudowaliśmy w lekcji 11.7. W lekcji 11.8 podmienimy je
            # na bardziej szczegółowy widok pojedynczego zamówienia.
            return redirect("szczegoly_zamowienia_pracownik", id_zamowienia=zamowienie.pk)
    else:
        # Przy wejściu metodą GET pokazujemy formularz wypełniony obecnym statusem.
        formularz = ZmianaStatusuForm(instance=zamowienie)

    return render(request, "sklep_aplikacja/zmien_status.html", {
        "formularz": formularz,
        "zamowienie": zamowienie,
    })

@login_required
def historia_zamowien(request):
    klient = get_object_or_404(Klient, uzytkownik=request.user)
    zamowienia = Zamowienie.objects.filter(klient=klient).order_by("-data_zamowienia")
    return render(request, "sklep_aplikacja/historia_zamowien.html", {
        "zamowienia": zamowienia,
    })

@login_required
def szczegoly_zamowienia(request, id_zamowienia):
    zamowienie = get_object_or_404(Zamowienie, pk=id_zamowienia)
    # Spójnie z 2.7, 11.3, 11.4, 11.6 – pobranie klienta przez get_object_or_404.
    # Pracownik bez profilu Klient dostanie tu 404 (a nie crash z AttributeError).
    klient = get_object_or_404(Klient, uzytkownik=request.user)
    if zamowienie.klient_id != klient.pk:
        raise Http404
    return render(request, "sklep_aplikacja/szczegoly_zamowienia.html", {
        "zamowienie": zamowienie,
        "pozycje": zamowienie.pozycje.select_related("produkt"),
    })

@login_required
def panel_klienta(request):
    # Spójnie z 2.7 i 11.3 – pobranie klienta przez get_object_or_404.
    # Zalogowany pracownik bez profilu Klient zobaczy 404 zamiast crashu z AttributeError.
    klient = get_object_or_404(Klient, uzytkownik=request.user)
    zamowienia = Zamowienie.objects.filter(klient=klient).order_by("-data_zamowienia")

    return render(request, "sklep_aplikacja/panel_klienta.html", {
        "klient": klient,
        "zamowienia": zamowienia,
    })


@user_passes_test(jest_pracownikiem)
def panel_pracownika(request):
    nowe = Zamowienie.objects.filter(status="nowe").count()
    oplacone = Zamowienie.objects.filter(status="oplacone").count()
    wyslane = Zamowienie.objects.filter(status="wyslane").count()
    return render(request, "sklep_aplikacja/panel_pracownika.html", {
        "liczba_nowych": nowe,
        "liczba_oplaconych": oplacone,
        "liczba_wyslanych": wyslane,
    })

@login_required
@user_passes_test(jest_pracownikiem)
def lista_zamowien_pracownik(request):
    status = request.GET.get("status")
    zamowienia = Zamowienie.objects.select_related("klient__uzytkownik").order_by("-data_zamowienia")
    if status:
        zamowienia = zamowienia.filter(status=status)

    statusy = ["nowe", "oplacone", "wyslane", "zrealizowane", "anulowane"]
    return render(request, "sklep_aplikacja/lista_zamowien_pracownik.html", {
        "zamowienia": zamowienia,
        "statusy": statusy,
        "status_aktywny": status,
    })

@login_required
@user_passes_test(jest_pracownikiem)
def szczegoly_zamowienia_pracownik(request, id_zamowienia):
    zamowienie = get_object_or_404(Zamowienie, pk=id_zamowienia)
    if request.method == "POST":
        formularz = ZmianaStatusuForm(request.POST, instance=zamowienie)
        if formularz.is_valid():
            formularz.save()
            return redirect("szczegoly_zamowienia_pracownik", id_zamowienia=zamowienie.pk)
    else:
        formularz = ZmianaStatusuForm(instance=zamowienie)

    return render(request, "sklep_aplikacja/szczegoly_zamowienia_pracownik.html", {
        "zamowienie": zamowienie,
        "pozycje": zamowienie.pozycje.select_related("produkt"),
        "formularz": formularz,
    })


def koszyk(request):
    # Sam podgląd koszyka – metoda GET jest tu w porządku, nic nie zmieniamy.
    k = Koszyk(request)
    return render(request, "sklep_aplikacja/koszyk.html", {
        "pozycje": k.pozycje(),
        "suma": k.suma(),
    })


@require_POST
def dodaj_do_koszyka(request, id_produktu):
    # @require_POST blokuje wywołanie tego widoku przez GET. Bez tego ktoś mógłby
    # wstawić w sieci link <a href="/koszyk/dodaj/3/"> i każdy, kto go kliknie,
    # niechcący zaktualizuje swój koszyk.
    produkt = get_object_or_404(Produkt, pk=id_produktu, czy_aktywny=True)
    k = Koszyk(request)
    k.dodaj(produkt.pk)
    messages.success(request, f"Dodano {produkt.nazwa_produktu} do koszyka.")
    return redirect("koszyk")


@require_POST
def usun_z_koszyka(request, id_produktu):
    k = Koszyk(request)
    k.usun(id_produktu)
    messages.info(request, "Usunięto produkt z koszyka.")
    return redirect("koszyk")

@login_required
@require_POST
def zloz_zamowienie(request):
    k = Koszyk(request)
    if not k.koszyk:
        messages.warning(request, "Twój koszyk jest pusty.")
        return redirect("lista_produktow")

    # Spójnie z 2.7 i 11.3 – pobranie klienta przez get_object_or_404.
    klient = get_object_or_404(Klient, uzytkownik=request.user)

    pozycje_koszyka = k.pozycje()

    # Walidacja PRZED transakcją: jeśli któregoś produktu brakuje,
    # nie tworzymy w ogóle zamówienia w bazie.
    for poz in pozycje_koszyka:
        if poz["produkt"].stan_magazynowy < poz["ilosc"]:
            messages.error(
                request,
                f"Brak wystarczającej liczby sztuk: {poz['produkt'].nazwa_produktu}.",
            )
            return redirect("koszyk")

    adres = f"{klient.ulica}, {klient.kod_pocztowy} {klient.miasto}"

    # Transakcja oznacza: albo zapiszą się wszystkie elementy zamówienia, albo żaden.
    with transaction.atomic():
        zamowienie = Zamowienie.objects.create(
            klient=klient,
            status="nowe",
            adres_dostawy=adres,
            wartosc_zamowienia=Decimal("0.00"),
        )

        suma = Decimal("0.00")
        for poz in pozycje_koszyka:
            produkt = poz["produkt"]
            ilosc = poz["ilosc"]
            cena = Decimal(produkt.cena_produktu)

            PozycjaZamowienia.objects.create(
                zamowienie=zamowienie,
                produkt=produkt,
                ilosc=ilosc,
                cena_jednostkowa=cena,
            )
            produkt.stan_magazynowy -= ilosc
            produkt.save(update_fields=["stan_magazynowy"])
            suma += cena * ilosc

        zamowienie.wartosc_zamowienia = suma
        zamowienie.save(update_fields=["wartosc_zamowienia"])
    
    wyslij_potwierdzenie_zamowienia(zamowienie)

    k.wyczysc()
    messages.success(request, f"Zamówienie #{zamowienie.pk} złożone. Wysłaliśmy potwierdzenie e-mailem.")
    return redirect("szczegoly_zamowienia", id_zamowienia=zamowienie.pk)

@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def rejestracja_klienta(request):
    if request.method == "POST":
        form = RejestracjaKlientaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            # Przekierowujemy na nazwany URL "login" z django.contrib.auth.urls.
            return redirect("login")
    else:
        form = RejestracjaKlientaForm()

    return render(request, "sklep_aplikacja/rejestracja.html", {"form": form})

@require_POST
def ustaw_ilosc_w_koszyku(request, produkt_id):
    produkt = get_object_or_404(Produkt, id=produkt_id, czy_aktywny=True)

    # 1) Walidacja typu: użytkownik mógł wpisać "abc" w <input> albo
    #    sfabrykować request bez pola "ilosc". Bez try/except dostalibyśmy
    #    ValueError -> HTTP 500.
    try:
        nowa_ilosc = int(request.POST.get("ilosc", "1"))
    except (TypeError, ValueError):
        messages.error(request, "Podaj poprawną liczbę sztuk.")
        return redirect("koszyk")

    # 2) Walidacja zakresu: po typie sprawdzamy, czy liczba jest sensowna.
    if nowa_ilosc < 1:
        messages.error(request, "Ilość musi być większa od zera.")
        return redirect("koszyk")

    if nowa_ilosc > produkt.stan_magazynowy:
        messages.error(request, "Nie ma tylu sztuk w magazynie.")
        return redirect("koszyk")

    koszyk = request.session.get("koszyk", {})
    koszyk[str(produkt_id)] = nowa_ilosc
    request.session["koszyk"] = koszyk
    request.session.modified = True
    return redirect("koszyk")

@require_POST
def wyloguj(request):
    # 1) Zapamiętaj koszyk PRZED czyszczeniem sesji.
    koszyk_zapisany = request.session.get("koszyk", {})
    auth_logout(request)
    # 2) auth_logout() rotuje session_key i wywołuje flush. Po tym mamy nową, pustą sesję.
    request.session["koszyk"] = koszyk_zapisany
    request.session.modified = True
    return redirect("strona_glowna")


