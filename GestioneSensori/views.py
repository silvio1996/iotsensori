from datetime import datetime
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, ProtectedError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from GestioneSensori.decorators import impianto_attivo_required, staff_required
from GestioneSensori.forms import ImpiantoForm, SensoreForm, UtenteForm, SensoreEditForm, UtenteEditForm, \
    SpostaSensoreForm, TipoSensoreForm, MarcaSensoreForm
from GestioneSensori.models import Impianto, Utente, Sensore, Rilevazione, Installazione, TipoSensore, \
    Eccezione, MarcaSensore


def get_data(req, type_req):
    return req.POST if type_req != 'GET' else req.GET


def super_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


@login_required
def panel(request):
    return render(request, 'panel.html')


@login_required
def impianti(request):
    list_impianti = request.user.get_impianti()
    return render(request, 'impianti/impianti.html', {
        'impianti': list_impianti,
    })


@login_required
def attiva_impianto(request):
    imp = get_object_or_404(Impianto, id=get_data(request, 'GET')['id'])
    if not request.user.is_staff and imp not in list(request.user.get_impianti()):
        raise PermissionDenied('Non puoi selezionare come attivo un impianto non posseduto.')
    utente = get_object_or_404(Utente, id=request.user.id)
    utente.impianto_attivo = get_object_or_404(Impianto, id=get_data(request, 'GET')['id'])
    utente.save()
    return HttpResponseRedirect(reverse('impianti'))


@login_required
@staff_required
def elimina_impianto(request):
    get_object_or_404(Impianto, id=get_data(request, 'GET')['id']).delete()
    return HttpResponseRedirect(reverse('impianti'))


@login_required
@staff_required
def aggiungi_impianto(request):
    if request.method == 'POST':
        form = ImpiantoForm(get_data(request, 'POST'))
        if form.is_valid():
            imp = form.save()
            return super_redirect('dettagli_impianto', id=str(imp.id))
    else:
        form = ImpiantoForm()
    return render(request, 'impianti/aggiungi_impianto.html', {
        'form': form
    })


@login_required
def dettagli_impianto(request):
    imp = get_object_or_404(Impianto, id=get_data(request, 'GET')['id'])
    if not request.user.is_staff and imp not in list(request.user.get_impianti()):
        raise PermissionDenied('Non puoi selezionare come attivo un impianto non posseduto.')
    return render(request, 'impianti/dettagli_impianto.html', {
        'impianto': imp
    })


@login_required
@staff_required
def modifica_impianto(request):
    imp = get_object_or_404(Impianto, id=get_data(request, 'GET')['id'])
    if request.method == 'POST':
        form = ImpiantoForm(get_data(request, 'POST'), instance=imp)
        if form.is_valid():
            form.save()
            return super_redirect('dettagli_impianto', id=str(imp.id))
    else:
        form = ImpiantoForm(instance=imp)
        return render(request, 'impianti/modifica_impianto.html', {
            'form': form,
            'impianto': imp
        })


@login_required
@impianto_attivo_required
def sensori(request):
    list_sensori = request.user.impianto_attivo.get_sensori()
    return render(request, 'sensori/sensori.html', {
        'sensori': list_sensori,
    })


@login_required
@impianto_attivo_required
def dettagli_sensore(request):
    id_sensore_get = get_data(request, 'GET')['id_sensore']
    sensore = get_object_or_404(Sensore, id=id_sensore_get)
    if sensore.get_impianto().user != request.user:
        raise PermissionDenied('Non puoi frugare nei sensori di altri utenti!')
    return render(request, 'sensori/dettagli_sensore.html', {
        'sensore': sensore
    })


@login_required
@staff_required
@impianto_attivo_required
def elimina_sensore(request):
    sensore = get_object_or_404(Sensore, id=get_data(request, 'GET')['id'])
    id_imp = request.user.impianto_attivo_id
    installazione = Installazione.objects.filter(
        impianto=id_imp, sensore__id=sensore.id,
        impianto__installazione__data_fine__isnull=True).latest('id')
    installazione.data_fine = timezone.make_aware(
        datetime.now(),
        timezone.get_current_timezone()
    )
    installazione.save()
    return HttpResponseRedirect(reverse('sensori'))


@login_required
@staff_required
@impianto_attivo_required
def aggiungi_sensore(request):
    tipi_sensori = TipoSensore.objects.all()
    marche_sensori = MarcaSensore.objects.all()
    if request.method == 'POST':
        form = SensoreForm(get_data(request, 'POST'))
        if form.is_valid():
            sensore = form.save()
            sensore.set_installazione(request.user.impianto_attivo)
            return HttpResponseRedirect(reverse('sensori'))
    else:
        form = SensoreForm()
    return render(request, 'sensori/aggiungi_sensore.html', {
        'form': form,
        'formts': TipoSensoreForm(),
        'formms': MarcaSensoreForm(),
        'tipi_sensori': tipi_sensori,
        'marche_sensori': marche_sensori
    })


@login_required
@staff_required
@impianto_attivo_required
def modifica_sensore(request):
    sensore = get_object_or_404(Sensore, id=get_data(request, 'GET')['id_sensore'])
    if request.method == 'POST':
        form = SensoreEditForm(get_data(request, 'POST'), instance=sensore)
        if form.is_valid():
            form.save()
            return super_redirect('dettagli_sensore', id_sensore=str(sensore.id))
    else:
        form = SensoreEditForm(instance=sensore)
        return render(request, 'sensori/modifica_sensore.html', {
            'form': form,
            'sensore': sensore,
            'impianti': Impianto.objects.filter(user=request.user.id)
        })


@login_required
@staff_required
@impianto_attivo_required
def sposta_sensore(request):
    sensore = get_object_or_404(Sensore, id=get_data(request, 'GET')['id_sensore'])
    all_impianti = request.user.get_impianti()
    if request.method == 'POST':
        form = SpostaSensoreForm(get_data(request, 'POST'), impianti=all_impianti)
        if form.is_valid():
            imp_post = get_data(request, 'POST')['imp']
            imp_attuale = request.user.impianto_attivo
            if str(imp_attuale.id) != str(imp_post):
                installazione = sensore.get_last_installazione()
                installazione.data_fine = timezone.make_aware(
                    datetime.now(),
                    timezone.get_current_timezone()
                )
                installazione.save()
                Installazione.objects.create(
                    impianto=Impianto.objects.get(id=imp_post),
                    sensore=sensore,
                    data_inizio=timezone.make_aware(
                        datetime.now(),
                        timezone.get_current_timezone()
                    )
                )
            return HttpResponseRedirect(reverse('sensori'))
    else:
        form = SpostaSensoreForm(impianti=all_impianti)
    return render(request, 'sensori/sposta_sensore.html', {
        'form': form,
        'sensore': sensore
    })


@login_required
@staff_required
@impianto_attivo_required
def sensori_eliminati(request):
    list_sensori_eliminati = request.user.impianto_attivo.get_sensori_eliminati()
    return render(request, 'sensori/sensori_eliminati.html', {
        'sensori_eliminati': list_sensori_eliminati
    })


@login_required
@staff_required
@impianto_attivo_required
def ripristina_sensore(request):
    sensore = get_object_or_404(Sensore, id=get_data(request, 'GET')['id_sensore'])
    ultima_installazione = Installazione.objects.filter(sensore=sensore.id).last()
    ultima_installazione.data_fine = None
    ultima_installazione.save()
    return HttpResponseRedirect(reverse('sensori'))


@login_required
@staff_required
@impianto_attivo_required
def elimina_sensore_fisicamente(request):
    sensore = get_object_or_404(Sensore, id=get_data(request, 'GET')['id_sensore'])
    sensore.delete()
    return HttpResponseRedirect(reverse('sensori_eliminati'))


@login_required
@staff_required
def aggiungi_tipo_sensore(request):
    if request.method == 'POST':
        form = TipoSensoreForm(get_data(request, 'POST'))
        if TipoSensore.objects.filter(tipo=get_data(request, 'POST')['tipo']).exists():
            messages.error(request, 'Tipo sensore esistente!')
        if form.is_valid():
            form.save()
            messages.success(request, 'Aggiunto con successo!')
    return render(request, 'sensori/aggiungi_tipo_sensore.html', {
        'form': TipoSensoreForm()
    })


@login_required
@staff_required
def elimina_tipo_sensore(request):
    get_object_or_404(TipoSensore, id=get_data(request, 'GET')['id']).delete()
    return HttpResponseRedirect(reverse('aggiungi_sensore'))


@login_required
@staff_required
def aggiungi_marca_sensore(request):
    if request.method == 'POST':
        form = MarcaSensoreForm(get_data(request, 'POST'))
        if MarcaSensore.objects.filter(marca=get_data(request, 'POST')['marca']).exists():
            messages.error(request, 'Marca già esistente!')
        if form.is_valid():
            form.save()
            messages.success(request, 'Aggiunto con successo!')
    return render(request, 'sensori/aggiungi_marca_sensore.html', {
        'form': MarcaSensoreForm()
    })


@login_required
@staff_required
def elimina_marca_sensore(request):
    get_object_or_404(MarcaSensore, id=get_data(request, 'GET')['id']).delete()
    return HttpResponseRedirect(reverse('aggiungi_sensore'))


@login_required
@impianto_attivo_required
def rilevazioni(request):
    id_sensore_get = get_data(request, 'GET')['id_sensore']
    sensore = get_object_or_404(Sensore, id=id_sensore_get)
    list_rilevazioni = sensore.get_rilevazioni()
    return render(request, 'rilevazioni/rilevazioni.html', {
        'id_sensore': id_sensore_get,
        'rilevazioni': list_rilevazioni,
    })


@login_required
@impianto_attivo_required
def elimina_rilevazione(request):
    ril = Rilevazione.objects.get(id=get_data(request, 'GET')['id'])
    sensore = Sensore.objects.get(id=ril.sensore)
    imp_sensore = sensore.impianto.get(installazione__data_fine__isnull=True)
    if request.user.impianto_attivo_id != imp_sensore.id:
        raise PermissionDenied('Non puoi operare su sensori che non sono presenti nell\'impianto attivo scelto.')
    ril.delete()
    return super_redirect('rilevazioni', id_sensore=str(sensore.id))


@login_required
@impianto_attivo_required
def dettagli_rilevazione(request):
    ril = Rilevazione.objects.get(id=get_data(request, 'GET')['id'])
    if ril.sensore.get_impianto().user != request.user:
        raise PermissionDenied('Non puoi frugare nelle rilevazioni di altri sensori che non ti appartengono!')
    return render(request, 'rilevazioni/dettagli_rilevazione.html', {
        'rilevazione': ril
    })


@login_required
@staff_required
def utenti(request):
    azienda = request.user.azienda
    list_utenti = azienda.get_utenti()
    return render(request, 'utenti/utenti.html', {
        'utenti': list_utenti,
    })


@login_required
@staff_required
def elimina_utente(request):
    utente = get_object_or_404(Utente, id=get_data(request, 'GET')['id'])
    if utente.is_superuser:
        raise PermissionDenied('Non puoi cancellare un utente superadmin!')
    utente.delete()
    return redirect('utenti')


@login_required
@staff_required
def dettagli_utente(request):
    utente = get_object_or_404(Utente, id=get_data(request, 'GET')['id'])
    token = utente.get_token()
    return render(request, 'utenti/dettagli_utente.html', {
        'utente': utente,
        'token': token
    })


@login_required
@staff_required
def validate_username(request):
    username = get_data(request, 'GET').get('username', None)
    data = {'is_taken': Utente.objects.filter(username__iexact=username).exists()}
    if data['is_taken']:
        data['error_message'] = 'Username non disponibile.'
    return JsonResponse(data)


@login_required
@staff_required
def aggiungi_utente(request):
    if request.method == 'POST':
        form = UtenteForm(get_data(request, 'POST'))
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/utenti')
    else:
        form = UtenteForm()
    return render(request, 'utenti/aggiungi_utente.html', {
        'form': form
    })


@login_required
@staff_required
def modifica_utente(request):
    utente = get_object_or_404(Utente, id=get_data(request, 'GET')['id'])
    if request.method == 'POST':
        form = UtenteEditForm(get_data(request, 'POST'), instance=utente)
        if form.is_valid():
            utente = form.save(commit=False)
            utente.set_password(get_data(request, 'POST')['password2'])
            utente.data_nascita = datetime.strptime(get_data(request, 'POST')['data_nascita'], '%d/%m/%Y')
            utente.save()
            return super_redirect('dettagli_utente', id=str(utente.id))
    else:
        form = UtenteEditForm(instance=utente)
        return render(request, 'utenti/modifica_utente.html', {
            'form': form,
            'utente': utente,
            'data_n_format': utente.data_nascita.strftime('%d/%m/%Y')
        })


@login_required
@impianto_attivo_required
def dashboard(request):
    eccezioni = Eccezione.objects.filter(
        sensore__impianto=request.user.impianto_attivo_id).order_by('-id').distinct()
    list_id_ecc = [ril.id for ril in eccezioni]
    andamento_eccezioni = Eccezione.objects.all().filter(id__in=list_id_ecc) \
        .values('sensore').annotate(num=Count('id'))

    return render(request, 'dashboard.html', {
        'ril_ecc': eccezioni[:10],
        'ril_and': andamento_eccezioni
    })
