from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse


def impianto_attivo_required(func):
    def inner(request):
        if request.user.impianto_attivo is None:
            return redirect(reverse('impianti'))
        return func(request)

    return inner


def staff_required(func):
    def inner(request):
        if not request.user.is_staff:
            raise PermissionDenied('Non sei autorizzato! Solo lo staff può!')
        return func(request)

    return inner

