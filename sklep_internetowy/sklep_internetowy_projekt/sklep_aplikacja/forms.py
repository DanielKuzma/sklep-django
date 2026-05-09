from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Klient, ProfilUzytkownika, Zamowienie

class ZmianaStatusuForm(forms.ModelForm):
    class Meta:
        # ModelForm buduje formularz na podstawie modelu Zamowienie.
        model = Zamowienie
        # Użytkownik może zmienić tylko status, nie klienta ani wartości zamówienia.
        fields = ["status"]


class RejestracjaKlientaForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    imie = forms.CharField(max_length=150, required=True, label="Imię")
    nazwisko = forms.CharField(max_length=150, required=True, label="Nazwisko")

    class Meta:
        model = User
        # W Meta.fields wymieniamy WYŁĄCZNIE pola modelu User.
        # imie i nazwisko są zadeklarowane wyżej jako osobne pola formularza –
        # Django i tak doda je do gotowego HTML-a. Wpisanie ich tu spowodowałoby
        # FieldError: Unknown field(s) (imie, nazwisko) specified for User.
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        # UserCreationForm zapisuje hasło bezpiecznie, ale nie zapisuje
        # imienia, nazwiska ani e-maila – musimy zrobić to sami.
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["imie"]
        user.last_name = self.cleaned_data["nazwisko"]
        if commit:
            user.save()
            # Tworzymy też pusty profil klienta. Adres uzupełnimy później.
            Klient.objects.create(uzytkownik=user)
            # I profil użytkownika z rolą "klient". Bez tego kod sprawdzający
            # rolę (np. user.profiluzytkownika.rola w menu) nie miałby do czego
            # się odwołać i milcząco zwracałby False.
            ProfilUzytkownika.objects.create(uzytkownik=user, rola="klient")
        return user