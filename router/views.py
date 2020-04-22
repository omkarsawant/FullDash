from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from closets.models import Closets
from interactive import base_system
from overview.models import Overview

from . import base_router
from .forms import WanBrownForm, WanGreenForm
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
    if not router_records and overview_record.project_type == Overview.ProjectTypeChoices.GREENFIELD:
        return redirect(reverse('wan_green', kwargs={'id': kwargs['id']}))
    return redirect(reverse('wan_brown', kwargs={'id': kwargs['id']}))


def wan_brown_view(request, *args, **kwargs):
    router_1_initial = dict()
    router_2_initial = dict()
    obj = type('', (object,), {})()
    template_name = 'wan_brown.html'
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    mdf_closets = base_system.get_mdf_closets(closets_records)
    router_records = base_system.get_device_records(Router, mdf_closets)
    obj.router_hostnames = list()
    if not router_records:
        obj.router_hostnames = base_system.get_mdf_device_hostnames(
            overview_record, mdf_closets, Router)
    else:
        router_1_initial = router_records[0]
        router_2_initial = router_records[1]
        obj.router_hostnames.append(router_records[0].hostname)
        obj.router_hostnames.append(router_records[1].hostname)
    if request.method == 'GET':
        obj.router_forms = list()
        obj.router_forms.append(WanBrownForm(
            instance=router_1_initial, prefix='router_1'))
        obj.router_forms.append(WanBrownForm(
            instance=router_2_initial, prefix='router_2'))
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        WanBrownForm(request.POST, prefix='router_1')
        if 'router_1' in request.POST:
            print('here')
        # TODO: finish the code!
        # TODO: put message in overview about success
        pass


def wan_green_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'wan_green.html'
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    mdf_closets = base_system.get_mdf_closets(closets_records)
    obj.router_hostnames = base_system.get_mdf_device_hostnames(
        overview_record, mdf_closets, Router)
    if request.method == 'GET':
        obj.form = WanGreenForm()
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        wan_green_query_dict = dict(request.POST)
        router_1_query_dict = QueryDict(mutable=True)
        router_2_query_dict = QueryDict(mutable=True)
        for key, value in wan_green_query_dict.items():
            if key in ['csrfmiddlewaretoken']:
                continue
            if len(value) == 1:
                router_1_query_dict.__setitem__(key, value[0])
                router_2_query_dict.__setitem__(key, value[0])
            else:
                router_1_query_dict.__setitem__(key, value[0])
                router_2_query_dict.__setitem__(key, value[1])
        router_1_form = WanGreenForm(router_1_query_dict)
        router_2_form = WanGreenForm(router_2_query_dict)
        if(router_1_form.is_valid() and router_2_form.is_valid()):
            # TODO: finish the code with cleaned_data
            # TODO: put message in overview about success
            if len(mdf_closets) == 1:
                base_router.make_model(mdf_closets[0])
                base_router.make_model(mdf_closets[0])
            else:
                base_router.make_model(mdf_closets[0])
                base_router.make_model(mdf_closets[1])
            base_system.activate_modal(obj, 'WAN_GREEN_SUCCESS')
        obj.form = WanGreenForm(request.POST)
        for error in router_1_form.errors.values():
            messages.error(request, error)
        for error in router_2_form.errors.values():
            messages.error(request, error)
        return render(request, template_name, {'obj': obj})
