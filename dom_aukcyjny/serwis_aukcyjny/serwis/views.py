from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, View, TemplateView, DetailView, FormView, UpdateView
from .forms import RejestracjaKlientaForm, MakeNewOfferForm, AddAuctionForm
from .models import Aukcja, Oferta, Uzytkownik, Platnosc
from datetime import date
from .emails import wyslij_potwierdzenie_platnosci


# Create your views here.

class StartingPage(TemplateView):
    template_name = "serwis/start_page.html"

def sing_up(request):
    if request.method == "POST":
        form = RejestracjaKlientaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            return redirect("login")
    else:
        form = RejestracjaKlientaForm()
    return render(request, "registration/sing_up.html", {"form" : form})

class AuctionList(ListView):
    model = Aukcja
    context_object_name = "all_auctions"
    template_name = "serwis/all_auction.html"
    queryset = Aukcja.objects.filter(status = "Aktywny")

# to zmienic na class AuctionDetail(View)
    #def get i post
class AuctionDetail(LoginRequiredMixin, View):
    def get(self, request, slug):
        auction_detail = get_object_or_404(Aukcja, slug=slug)
        last = auction_detail.oferty.order_by("-data_zlozenia_oferty").first()
        date_ = (auction_detail.data_zakonczenia <= date.today())

        if last:
            last_offer = last.oferowana_cena
            is_wining = last.kupujacy.username
        else:
            last_offer = auction_detail.cena_wywolawcza
            is_wining = None

        return render(request, "serwis/auction_detail.html", {
            "is_wining" : is_wining,
            "auction_detail" : auction_detail,
            "last_offer" : last_offer,
            "form": MakeNewOfferForm(),
            "is_end" : date_,
        })
    
    def post(self, request, slug):
        auction_detail = get_object_or_404(Aukcja, slug=slug)

        form = MakeNewOfferForm(request.POST)
        form.instance.aukcja = auction_detail

        if form.is_valid():
                new_offer = form.save(commit=False)
                new_offer.kupujacy = request.user
                new_offer.save()
                return redirect("my_biddings")
        
        
        last = auction_detail.oferty.order_by("-data_zlozenia_oferty").first()
        last_offer = last.oferowana_cena if last else auction_detail.cena_wywolawcza
        return render(request, "serwis/auction_detail.html", {
            "auction_detail": auction_detail,
            "last_offer" : last_offer,
            "form" : form,
        })

class  MyProfile(LoginRequiredMixin, TemplateView):
    template_name = "serwis/client_profile.html"
    model = Uzytkownik
    context_object_name = "my_profile"

class  AllMyOffers(LoginRequiredMixin, ListView):
    template_name = "serwis/client_offers.html"
    context_object_name = "my_offers"
    model = Aukcja 

    def get_queryset(self): 
        data = Aukcja.objects.filter(sprzedajacy__uzytkownik = self.request.user)
        return data.order_by("status")

class UserBiddingAuctions(LoginRequiredMixin, ListView):
    template_name = "serwis/client_bidding_auctions.html"
    context_object_name = "my_biddings"
    model = Aukcja 

    def get_queryset(self): 
        data = Aukcja.objects.filter(oferty__kupujacy=self.request.user)
        return data.distinct()
    
class AddAuction(LoginRequiredMixin, CreateView):
    model = Aukcja
    form_class = AddAuctionForm
    template_name = "serwis/add_auction.html"

    def get_success_url(self):
        return reverse("my_offers")    
    
    def form_valid(self, form):
        form.instance.sprzedajacy = self.request.user.uzytkownik
        return super().form_valid(form)
    
class ClientMyInvoices(LoginRequiredMixin, ListView):
    model = Platnosc
    template_name = "serwis/client_my_invoices.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return Platnosc.objects.filter(platnik__uzytkownik=self.request.user).order_by('status_platnosci')

class ClientPayInvoice(LoginRequiredMixin, UpdateView):
    model = Platnosc
    fields = ['metoda_platnosc']
    template_name = "serwis/client_pay_invoice.html"

    def get_success_url(self):
        return reverse("client_invoices")    

    def get_queryset(self):
        return Platnosc.objects.filter(
            platnik__uzytkownik=self.request.user, 
            status_platnosci="Nie Zaplacone"
        )
    
# Opsługa panelu uzytkowniak 

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or  self.request.user.profiluzytkownika.rola == "Pracownik"

class StaffAuctionsToClose(StaffRequiredMixin, ListView):
    model = Aukcja
    template_name = "serwis/staff_auctions_to_close.html"
    context_object_name = "auctions" 

    def get_queryset(self):
        return Aukcja.objects.filter(status="Aktywny", data_zakonczenia__lt=date.today())

class StaffIssueInvoice(StaffRequiredMixin, View):
    def post(self, request, pk):
        aukcja = get_object_or_404(Aukcja, pk=pk)
        aukcja.wystaw_rachunek() 
        return redirect('staff_auctions') 

class StaffPendingPayments(StaffRequiredMixin, ListView):
    model = Platnosc
    template_name = "serwis/staff_pending_payments.html"
    context_object_name = "payments"

    def get_queryset(self):
        return Platnosc.objects.filter(status_platnosci="Nie Zaplacone").exclude(metoda_platnosc__isnull=True)

class StaffConfirmPayment(StaffRequiredMixin, View):
    def post(self, request, pk):
        platnosc = get_object_or_404(Platnosc, pk=pk)
        platnosc.status_platnosci = "Zaplacone"
        platnosc.save()
        wyslij_potwierdzenie_platnosci(platnosc)
        return redirect('staff_payments')