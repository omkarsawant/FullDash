from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from closets.models import Closets
from interactive import base_system
from overview.models import Overview


def wan_landing_view(request, *args, **kwargs):
    intial = dict()
    obj = type('', (object,), {})()
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    print(not closets_records)
    if not closets_records:
        base_system.activate_modal(
            obj, 'Closets Closets Closets Closets', 'No closets have been defined for this network')
        return render(request, 'error.html', {'obj': obj})
    for closet_record in closets_records:
        if closet_record.category in ['mdf', 'mdf_idf']:
            pass
            # check if routers exist in MDF with flag
        pass
    # check if not exists + greenfield --> go to WAN form
    # check elseif not exists + brownfield --> create WAN
    # go to WAN list
    return redirect(reverse('url_name', kwargs={}))
