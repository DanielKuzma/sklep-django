from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Uzytkownik, ProfilUzytkownika, Oferta, Adres, Aukcja
from django.db import transaction

class RejestracjaKlientaForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    imie = forms.CharField(max_length=150, required=True, label="Imię")
    nazwisko = forms.CharField(max_length=150, required=True, label="Nazwisko")
    
    kraj = forms.CharField(max_length=100, required=True)
    miasto = forms.CharField(max_length=100, required=True)
    ulica = forms.CharField(max_length=255, required=True)
    kod_pocztowy = forms.CharField(max_length=6, required=True)
    numer_budynku = forms.CharField(max_length=10, required=True)
    numer_lokalu = forms.CharField(max_length=10, required=False)
    
    telefon = forms.CharField(max_length=11, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):

        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Konto z tym adresem e-mail już istnieje. "
                "Jeżeli to Twoje konto, użyj opcji „Nie pamiętam hasła”."
            )
        return email
    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["imie"]
        user.last_name = self.cleaned_data["nazwisko"]
        if commit:
            user.save()
            new_address = Adres.objects.create(
                kraj = self.cleaned_data["kraj"],
                miasto = self.cleaned_data["miasto"],
                ulica = self.cleaned_data["ulica"],
                kod_pocztowy = self.cleaned_data["kod_pocztowy"],
                numer_budynku = self.cleaned_data["numer_budynku"],
                numer_lokalu = self.cleaned_data["numer_lokalu"],

            )

            ProfilUzytkownika.objects.create(uzytkownik=user)

            Uzytkownik.objects.create(
                uzytkownik=user,
                adres = new_address,
                telefon = self.cleaned_data["telefon"] 
                )
        return user


class MakeNewOfferForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ["oferowana_cena"]

class AddAuctionForm(forms.ModelForm):
    class Meta:
        model = Aukcja
        fields = ["kategoria", "nazwa_produktu", "cena_wywolawcza", "data_zakonczenia", "opis", "image"]
        widgets = {
            'data_zakonczenia': forms.DateInput(attrs={
                'type': 'date',
            })
        }