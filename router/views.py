from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from closet.models import Closet
from interactive import base_system
from onboard.models import Site

from .forms import WanBrownForm, WanGreenForm
from .models import Router


def wan_brown_view(request, *args, **kwargs):
    router_1_initial = dict()
    router_2_initial = dict()
    obj = type('', (object,), {})()
    template_name = 'wan_brown.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    closet_records = Closet.objects.filter(site=site_record)
    mdf_closets = base_system.get_mdf_closets(closet_records)
    router_records = base_system.get_device_records(Router, mdf_closets)
    obj.router_hostnames = list()
    if not router_records:
        obj.router_hostnames = base_system.get_mdf_device_hostnames(
            site_record, mdf_closets, Router)
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
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        router_1_form = WanBrownForm(request.POST, prefix='router_1')
        router_2_form = WanBrownForm(request.POST, prefix='router_2')
        if(router_1_form.is_valid() and router_2_form.is_valid()):
            # TODO: make model
            pass
        # TODO: finish the code!
        # TODO: put message in overview about success


def wan_green_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'wan_green.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    mdf_closet_records = Closet.objects.filter(
        site=site_record, category__in=[Closet.CategoryChoices.MDF, Closet.CategoryChoices.MDF_IDF])
    obj.router_hostnames = base_system.get_mdf_device_hostnames(
        site_record, mdf_closet_records, Router)
    if request.method == 'GET':
        obj.form = WanGreenForm()
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
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
            router_1_record = router_1_form.save(commit=False)
            router_2_record = router_2_form.save(commit=False)
            router_1_record.hostname = obj.router_hostnames[0]
            router_2_record.hostname = obj.router_hostnames[1]
            if len(mdf_closet_records) == 1:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[0]
            else:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[1]
            router_1_record.save()
            router_2_record.save()
        obj.form = WanGreenForm(request.POST)
        base_system.set_form_errors(request, router_1_form, router_2_form)
        for error in router_1_form.errors.values():
            messages.error(request, error)
        for error in router_2_form.errors.values():
            messages.error(request, error)
        return render(request, template_name, {'obj': obj})


def wan_landing_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    closet_records = Closet.objects.filter(site=site_record)
    if not closet_records:
        base_system.generate_error(obj, 'NO_CLOSETS')
        return render(request, 'error.html', {'obj': obj})
    mdf_closets = base_system.get_mdf_closets(closet_records)
    if not mdf_closets:
        base_system.generate_error(obj, 'NO_MDF')
        return render(request, 'error.html', {'obj': obj})
    router_records = base_system.get_device_records(Router, mdf_closets)
    if not router_records and site_record.project_type == Site.ProjectTypeChoices.GREENFIELD:
        return redirect(reverse('wan_green', kwargs={'site_id': site_record.id}))
    return redirect(reverse('wan_brown', kwargs={'site_id': site_record.id}))
