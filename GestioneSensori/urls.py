"""GestioneSensori URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from rest_framework.authtoken import views as views_api

from GestioneSensori import views, api_views

urlpatterns = [
    # Url Sistema
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout, {'template_name': 'logout.html'}, name='logout'),
    # Url Principali
    url(r'^panel/$', views.panel, name='panel'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # Url Impianti
    url(r'^impianti/$', views.impianti, name='impianti'),
    url(r'^impianti/attiva/$', views.attiva_impianto, name='attiva_impianto'),
    url(r'^impianti/elimina/$', views.elimina_impianto, name='elimina_impianto'),
    url(r'^impianti/aggiungi/$', views.aggiungi_impianto, name='aggiungi_impianto'),
    url(r'^impianti/dettagli/$', views.dettagli_impianto, name='dettagli_impianto'),
    url(r'^impianti/modifica/$', views.modifica_impianto, name='modifica_impianto'),
    # Url Sensori
    url(r'^sensori/$', views.sensori, name='sensori'),
    url(r'^sensori/elimina/$', views.elimina_sensore, name='elimina_sensore'),
    url(r'^sensori/aggiungi/$', views.aggiungi_sensore, name='aggiungi_sensore'),
    url(r'^sensori/dettagli/$', views.dettagli_sensore, name='dettagli_sensore'),
    url(r'^sensori/modifica/$', views.modifica_sensore, name='modifica_sensore'),
    url(r'^sensori/sposta/$', views.sposta_sensore, name='sposta_sensore'),
    url(r'^sensori/eliminati/$', views.sensori_eliminati, name='sensori_eliminati'),
    url(r'^sensori/eliminati/ripristina/$', views.ripristina_sensore, name='ripristina_sensore'),
    url(r'^sensori/eliminati/elimina/$', views.elimina_sensore_fisicamente, name='elimina_sensore_fisicamente'),
    url(r'^sensori/tipi/aggiungi/$', views.aggiungi_tipo_sensore, name='aggiungi_tipo_sensore'),
    url(r'^sensori/tipi/elimina/$', views.elimina_tipo_sensore, name='elimina_tipo_sensore'),
    url(r'^sensori/marche/aggiungi/$', views.aggiungi_marca_sensore, name='aggiungi_marca_sensore'),
    url(r'^sensori/marche/elimina/$', views.elimina_marca_sensore, name='elimina_marca_sensore'),
    # Url Rilevazioni
    url(r'^rilevazioni/$', views.rilevazioni, name='rilevazioni'),
    url(r'^rilevazioni/elimina/$', views.elimina_rilevazione, name='elimina_rilevazione'),
    url(r'^rilevazioni/dettagli/$', views.dettagli_rilevazione, name='dettagli_rilevazione'),
    # Url Utenti
    url(r'^utenti/$', views.utenti, name='utenti'),
    url(r'^utenti/elimina/$', views.elimina_utente, name='elimina_utente'),
    url(r'^utenti/aggiungi/$', views.aggiungi_utente, name='aggiungi_utente'),
    url(r'^utenti/dettagli/$', views.dettagli_utente, name='dettagli_utente'),
    url(r'^utenti/modifica/$', views.modifica_utente, name='modifica_utente'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    # Url API General
    url(r'^get_auth_token/$', views_api.obtain_auth_token, name='get_auth_token'),
    # Url API Sensori
    url(r'^api/sensori/$', api_views.sensori_api, name='api_sensori'),
    url(r'^api/sensori/show/$', api_views.show_sensore_api, name='api_show_sensore'),
    # Url API Rilevazioni
    url(r'^api/rilevazioni/$', api_views.rilevazioni_api, name='api_rilevazioni'),
    url(r'^api/rilevazioni/show/$', api_views.show_rilevazione_api, name='api_show_rilevazione'),
    url(r'^api/rilevazioni/add/$', api_views.add_rilevazione_api, name='api_add_rilevazione'),
]
