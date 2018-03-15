from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from GestioneSensori.models import Sensore, Stringa, Rilevazione


class SensoreSerializer(ModelSerializer):
    class Meta:
        model = Sensore
        fields = ('id', 'tipo', 'marca', 'codice_errore')


class RilevazioneSerializer(ModelSerializer):
    class Meta:
        model = Rilevazione
        fields = ('stringa', 'sensore', 'dataora', 'valore', 'messaggio')


class StringaSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Stringa
        fields = ('stringa',)
