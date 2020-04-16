from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from closets.models import Closets
from interactive import base_system
from overview.models import Overview

from .models import Router


def wan_landing_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    if not closets_records:
        base_system.generate_error(obj, 'NO_CLOSETS')
        return render(request, 'error.html', {'obj': obj})
    mdf_closets = base_system.get_mdf_closets(closets_records)
    if not mdf_closets:
        base_system.generate_error(obj, 'NO_MDF')
        return render(request, 'error.html', {'obj': obj})
    router_records = base_system.get_device_records(Router, mdf_closets)
    if not router_records:
        if overview_record.project_type == Overview.ProjectTypeChoices.GREENFIELD:
            return redirect(reverse('wan_form', kwargs={'id': kwargs['id']}))
        else:
            if len(mdf_closets) == 1:
                pass
            else:
                pass
    # go to WAN list
    return redirect(reverse('wan_listing', kwargs={'id': kwargs['id']}))


def wan_listing_view(request, *args, **kwargs):
    pass


def wan_form_view(request, *args, **kwargs):
    pass
