from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, EmailField, CharField, Form, ChoiceField

from GestioneSensori.models import Impianto, Utente, Sensore, TipoSensore, MarcaSensore


class ImpiantoForm(ModelForm):
    class Meta:
        model = Impianto
        fields = ('name', 'city', 'address', 'user')


class SensoreForm(ModelForm):
    class Meta:
        model = Sensore
        exclude = ('impianto', 'data_creazione')


class SensoreEditForm(ModelForm):
    class Meta:
        model = Sensore
        exclude = ('impianto', 'id', 'data_creazione')


class UtenteForm(UserCreationForm):
    is_staff = ChoiceField(choices={
        (0, 'Cliente'),
        (1, 'Staff'),
    }, initial=0)
    sesso = ChoiceField(choices={
        ('M', 'Maschio'),
        ('F', 'Femmina'),
        ('A', 'Altro'),
    }, initial='M')

    class Meta:
        model = Utente
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'city', 'address', 'phone',
                  'is_staff', 'data_nascita', 'sesso')


class UtenteEditForm(ModelForm):
    is_staff = ChoiceField(choices={
        (0, 'Cliente'),
        (1, 'Staff'),
    }, initial=0)
    sesso = ChoiceField(choices={
        ('M', 'Maschio'),
        ('F', 'Femmina'),
        ('A', 'Altro'),
    }, initial='M')

    class Meta:
        model = Utente
        fields = ('username', 'first_name', 'last_name', 'email', 'city', 'address', 'phone',
                  'is_staff', 'data_nascita', 'sesso')


class PswDimenticataForm(Form):
    username = CharField(required=True)
    email = EmailField(required=True)


class SpostaSensoreForm(Form):
    def __init__(self, *args, **kwargs):
        self.impianti = kwargs.pop('impianti')
        super(SpostaSensoreForm, self).__init__(*args, **kwargs)
        self.fields['imp'] = ChoiceField(choices={
            (e.id, e.name) for e in self.impianti
        })

    imp = ChoiceField(choices={})


class TipoSensoreForm(ModelForm):
    class Meta:
        model = TipoSensore
        exclude = ()


class MarcaSensoreForm(ModelForm):
    class Meta:
        model = MarcaSensore
        exclude = ()
