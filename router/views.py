from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from closets.models import Closets
from interactive import base_system
from overview.models import Overview


def wan_landing_view(request, *args, **kwargs):
    intial = dict()
    obj = type('', (object,), {})()
    template_name = 'template.html'
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    for closet_record in closets_records:
        # check if routers exist in MDF with flag
        pass
    # check if not exists + greenfield --> go to WAN form
    # check elseif not exists + brownfield --> create WAN
    # go to WAN list
    return redirect(reverse('url_name', kwargs={}))
