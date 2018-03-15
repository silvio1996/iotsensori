from datetime import datetime, timedelta
from re import split

from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import connection
from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE, DateTimeField, DateField, \
    EmailField, ManyToManyField, OneToOneField, PROTECT
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token


class Azienda(Model):
    ragione_sociale = CharField(max_length=30)
    partita_iva = CharField(max_length=11, unique=True)
    email = EmailField(max_length=50)
    telefono = CharField(max_length=14)
    sito_web = CharField(max_length=100)

    def get_utenti(self):
        return Utente.objects.filter(azienda=self.id).order_by('last_name', 'first_name')

    class Meta:
        db_table = 'aziende'

    def __str__(self):
        return self.ragione_sociale


class Utente(AbstractUser):
    city = CharField(max_length=50)
    address = CharField(max_length=150)
    phone = CharField(max_length=15)
    data_nascita = DateField()
    impianto_attivo = OneToOneField('Impianto', on_delete=CASCADE, db_column='impianto_attivo', null=True)
    azienda = ForeignKey('Azienda', on_delete=CASCADE, db_column='azienda', default=1)
    sesso = CharField(max_length=1)

    def get_impianti(self):
        if self.is_staff:
            return Impianto.objects.all().order_by('-id')
        return Impianto.objects.filter(user=self.id).order_by('-id')

    def get_impianto_attivo(self):
        return Impianto.objects.get(id=self.impianto_attivo_id)

    def get_nome_impianto_attivo(self):
        try:
            name = Impianto.objects.get(id=self.impianto_attivo_id).name.capitalize()
        except Impianto.DoesNotExist:
            name = False
        return name

    def get_tipo(self):
        return 'Staff' if self.is_staff else 'Cliente'

    def get_token(self):
        return 'Token ' + str(Token.objects.get(user=self.id))

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'utenti'


class Impianto(Model):
    name = CharField(max_length=50)
    city = CharField(max_length=30)
    address = CharField(max_length=100, blank=True)
    user = ForeignKey('Utente', on_delete=CASCADE, db_column='user')
    data_creazione = DateTimeField(default=timezone.now)

    def get_sensori(self):
        return Sensore.objects.raw(
            'SELECT `sensori`.`id`, `sensori`.`tipo`, `sensori`.`marca`, `sensori`.`codice_errore` '
            'FROM `sensori` '
            'INNER JOIN `installazioni` ON (`sensori`.`id` = `installazioni`.`sensore`) '
            'WHERE (`installazioni`.`impianto` = %s AND installazioni.data_fine IS NULL)'
            'ORDER BY `sensori`.`data_creazione` DESC;',
            [self.id]
        )

    def get_sensori_eliminati(self):
        return Sensore.objects.filter(impianto__installazione__data_fine__isnull=False) \
            .exclude(id__in=self.get_sensori()).distinct()

    def get_num_sensori(self):
        return len(list(self.get_sensori()))

    def get_tipi_sensori(self):
        # return TipoSensore.objects.all().select_related().values('id', 'tipo')
        # .annotate(num=Count('sensore__id_sensore'))  -- (peccato che non vada bene xD)
        cursor = connection.cursor()
        cursor.execute(
            'SELECT DISTINCT `tipi_sensori`.`tipo`, COUNT(`sensori`.`tipo`) FROM `sensori` '
            'INNER JOIN `installazioni` ON (`sensori`.`id` = `installazioni`.`sensore`) '
            'INNER JOIN `tipi_sensori` ON (`sensori`.`tipo` = `tipi_sensori`.`id`) '
            'WHERE (`installazioni`.`impianto` = %s AND `installazioni`.`data_fine` IS NULL) '
            'GROUP BY tipo '
            'ORDER BY tipo;',
            [self.id]
        )
        return list(dict(tipo=result[0], num=result[1]) for result in cursor.fetchall())

    def get_sensori_attivi_24h(self):
        date_from = timezone.now() - timedelta(days=1)
        sensori24h = Sensore.objects.filter(impianto=self.id).distinct().select_related() \
            .filter(rilevazione__dataora__gte=date_from)
        return {'sensori24h': sensori24h, 'num': sensori24h.count()}

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'impianti'
        ordering = ['id']


class Installazione(Model):
    impianto = ForeignKey('Impianto', on_delete=CASCADE, db_column='impianto')
    sensore = ForeignKey('Sensore', on_delete=CASCADE, db_column='sensore')
    data_inizio = DateTimeField(default=timezone.now)  # default=datetime.now()
    data_fine = DateTimeField(null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'installazioni'


class TipoSensore(Model):
    tipo = CharField(max_length=30, unique=True)

    def __str__(self):
        return str(self.tipo)

    class Meta:
        db_table = 'tipi_sensori'
        ordering = ['id']


class MarcaSensore(Model):
    marca = CharField(max_length=30, unique=True)

    def __str__(self):
        return str(self.marca)

    class Meta:
        db_table = 'marche_sensori'
        ordering = ['id']


class Sensore(Model):
    id = CharField(max_length=30, primary_key=True)
    tipo = ForeignKey('TipoSensore', on_delete=PROTECT, db_column='tipo')
    marca = ForeignKey('MarcaSensore', on_delete=PROTECT, db_column='marca')
    codice_errore = CharField(max_length=30)
    impianto = ManyToManyField(Impianto, through='Installazione')
    data_creazione = DateTimeField(default=timezone.now)

    def get_last_installazione(self):
        return Installazione.objects.filter(impianto=self.impianto.last().id, sensore=self.id).last()

    def get_rilevazioni(self):
        return Rilevazione.objects.filter(
            sensore__id=self.id).exclude(valore__isnull=True).order_by('-dataora')

    def get_last_rilevazione(self):
        last_ril = Rilevazione.objects.filter(sensore__id=self.id).last()
        return last_ril if last_ril is not None else False

    def get_impianto(self):
        return self.impianto.last()

    def set_installazione(self, imp):
        Installazione.objects.create(
            impianto=imp,
            sensore=self,
        )

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'sensori'
        ordering = ['data_creazione']


class Stringa(Model):
    stringa = CharField(max_length=200)
    LEN_DATETIME = 14

    def get_info_stringa(self):
        string = str(self.stringa)
        split_space = split(' ', string)
        id_sensore = split_space[0]
        other = split_space[1]
        split_ln = split('(\d+)', other)
        numeric = split_ln[1]
        messaggio = split_ln[2]
        info = {
            'stringa': string,
            'id_sensore': id_sensore,
            'messaggio': messaggio,
            'numeric': numeric
        }
        sensore = Sensore.objects.get(id=info['id_sensore'])
        if numeric == str(sensore.codice_errore):
            return info
        valore = numeric[self.LEN_DATETIME::]
        dataora_str = numeric[0:self.LEN_DATETIME]
        dataora_obj = timezone.make_aware(
            datetime.strptime(dataora_str, '%Y%m%d%H%M%S'),
            timezone.get_current_timezone()
        )
        info.update({
            'dataora': dataora_obj,
            'valore': valore,
        })
        return info

    def traduci(self):
        info = self.get_info_stringa()
        sensore = Sensore.objects.get(id=info['id_sensore'])
        if info['numeric'] != str(sensore.codice_errore):
            ril = Rilevazione()
            ril.stringa_id = self.id
            ril.sensore_id = info['id_sensore']
            ril.messaggio = info.get('messaggio', 'Nessuno')
            ril.valore = info['valore']
            ril.dataora = info['dataora']
            ril.save()
        else:
            ecc = Eccezione()
            ecc.stringa_id = self.id
            ecc.sensore_id = info['id_sensore']
            ecc.messaggio = info.get('messaggio', 'Nessuno')
            ecc.save()

    def save(self, *args, **kwargs):
        super(Stringa, self).save(*args, **kwargs)
        self.traduci()

    def __str__(self):
        return self.stringa

    class Meta:
        db_table = 'stringhe'


class Eccezione(Model):
    stringa = OneToOneField('Stringa', on_delete=CASCADE, db_column='stringa')
    sensore = ForeignKey('Sensore', on_delete=CASCADE, db_column='sensore')
    messaggio = CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eccezioni'


class Rilevazione(Model):
    stringa = OneToOneField('Stringa', on_delete=CASCADE, db_column='stringa')
    sensore = ForeignKey('Sensore', on_delete=CASCADE, db_column='sensore')
    dataora = DateTimeField(auto_now=False, auto_now_add=False)
    valore = IntegerField()
    messaggio = CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'rilevazioni'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created and not kwargs.get('raw', False):
        Token.objects.create(user=instance)
