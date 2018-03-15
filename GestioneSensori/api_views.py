from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, parser_classes, authentication_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from GestioneSensori.models import Sensore, Rilevazione, TipoSensore, MarcaSensore
from GestioneSensori.serializers import SensoreSerializer, RilevazioneSerializer, StringaSerializer


@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def sensori_api(request):
    if request.method == 'GET':
        context = {'request': request}
        if request.user.is_staff:
            query = Sensore.objects.all()
        else:
            query = Sensore.objects.filter(impianto__user=request.user)
        serializer = SensoreSerializer(query, many=True, context=context)
        return Response([
            {
                'id_sensore': data['id'],
                'tipo': TipoSensore.objects.get(id=data['tipo']).tipo,
                'marca': MarcaSensore.objects.get(id=data['marca']).marca,
                'codice_errore': data['codice_errore']
            }
            for data in serializer.data
        ])


@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def show_sensore_api(request):
    if request.method == 'GET':
        id_sensore_get = request.GET.get("id_sensore", None)
        context = {'request': request}
        try:
            sensore = Sensore.objects.get(id=id_sensore_get)
            serializer = SensoreSerializer(sensore, context=context)
            data = serializer.data
            return Response({
                'id_sensore': data['id'],
                'tipo': TipoSensore.objects.get(id=data['tipo']).tipo,
                'marca': MarcaSensore.objects.get(id=data['marca']).marca,
                'codice_errore': data['codice_errore']
            })
        except Sensore.DoesNotExist:
            return Response({'error': 'id_sensore non presente nel sistema'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def rilevazioni_api(request):
    if request.method == 'GET':
        context = {'request': request}
        id_sensore_get = request.GET.get("id_sensore", None)
        try:
            sensore = Sensore.objects.get(id=id_sensore_get)
        except Sensore.DoesNotExist:
            return Response({'error': 'id_sensore non presente nel sistema'}, status=status.HTTP_400_BAD_REQUEST)
        rilevazioni = Rilevazione.objects.filter(sensore=id_sensore_get)
        serializer = RilevazioneSerializer(rilevazioni, many=True, context=context)
        return Response([
            {
                'id_sensore': sensore.id,
                'dataora': data['dataora'],
                'valore': data['valore'],
                'messaggio': data['messaggio'],
            }
            for data in serializer.data
        ])


@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def show_rilevazione_api(request):
    if request.method == 'GET':
        context = {'request': request}
        id_ril_get = request.GET.get("id", None)
        try:
            rilevazione = Rilevazione.objects.get(id=id_ril_get)
            serializer = RilevazioneSerializer(rilevazione, context=context)
            data = serializer.data
            return Response({
                'id_sensore': data['sensore'],
                'dataora': data['dataora'],
                'valore': data['valore'],
                'messaggio': data['messaggio'],
            })
        except Rilevazione.DoesNotExist:
            return Response({'error': 'rilevazione non presente nel sistema'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
@parser_classes((JSONParser,))
def add_rilevazione_api(request):
    if request.method == 'POST':
        context = {'request': request}
        serializer = StringaSerializer(data=request.data, context=context)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response({'status': 'fail', 'message': 'bad format'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'fail'}, status=status.HTTP_400_BAD_REQUEST)
