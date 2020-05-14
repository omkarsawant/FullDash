from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from ipaddress import IPv4Network

from closet.models import Closet
from interactive import base_system
from onboard.models import Site

from .forms import WanBrownForm, WanGreenForm, WanGreenSubForm
from .models import Router


def wan_brown_view(request, *args, **kwargs):
    router_1_initial = dict()
    router_2_initial = dict()
    obj = type('', (object,), {})()
    template_name = 'wan_brown.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    mdf_closet_records = Closet.objects.filter(site=site_record, category__in=[
                                               Closet.CategoryChoices.MDF, Closet.CategoryChoices.MDF_IDF])
    router_records = base_system.get_device_records(Router, mdf_closet_records)
    obj.router_hostnames = list()
    if not router_records:
        obj.router_hostnames = base_system.get_mdf_device_hostnames(
            site_record, mdf_closet_records, Router)
    else:
        router_1_initial = router_records[0]
        router_2_initial = router_records[1]
        obj.router_hostnames.append(router_records[0].hostname)
        obj.router_hostnames.append(router_records[1].hostname)
    obj.router_forms = list()
    if request.method == 'GET':
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
        obj.router_forms.append(WanBrownForm(request.POST, prefix='router_1'))
        obj.router_forms.append(WanBrownForm(request.POST, prefix='router_2'))
        if(obj.router_forms[0].is_valid() and obj.router_forms[1].is_valid()):
            router_1_record = obj.router_forms[0].save(commit=False)
            router_2_record = obj.router_forms[1].save(commit=False)
            if len(mdf_closet_records) == 1:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[0]
            else:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[1]
            router_1_record.save()
            router_2_record.save()
            site_record.signal_updated_wan = True
            site_record.save()
            return redirect(reverse('wan_brown', kwargs={'site_id': site_record.id}))
        base_system.set_form_errors(
            request, obj.router_forms[0], obj.router_forms[1])
        return render(request, template_name, {'obj': obj})


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
        obj.form = WanGreenForm(prefix='main')
        obj.sub_form = WanGreenSubForm(prefix='sub')
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.form = WanGreenForm(request.POST, prefix='main')
        obj.sub_form = WanGreenSubForm(request.POST, prefix='sub')
        if(obj.form.is_valid() and obj.sub_form.is_valid()):
            router_1_record = obj.form.save(commit=False)
            router_2_record = obj.sub_form.save(commit=False)
            router_1_record.hostname = obj.router_hostnames[0]
            router_2_record.hostname = obj.router_hostnames[1]
            router_1_record.isp_ip = str(IPv4Network(
                router_1_record.wan_link_cidr, False)[1])
            router_2_record.isp_ip = str(IPv4Network(
                router_2_record.wan_link_cidr, False)[1])
            router_2_record.local_asn = obj.form.cleaned_data['local_asn']
            if len(mdf_closet_records) == 1:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[0]
            else:
                router_1_record.closet = mdf_closet_records[0]
                router_2_record.closet = mdf_closet_records[1]
            router_1_record.save()
            router_2_record.save()
            site_record.signal_created_wan = True
            site_record.save()
            return redirect(reverse('wan_green', kwargs={'site_id': site_record.id}))
        base_system.set_form_errors(request, obj.form, obj.sub_form)
        return render(request, template_name, {'obj': obj})


def wan_landing_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    closet_records = Closet.objects.filter(site=site_record)
    if not closet_records:
        base_system.generate_error(obj, 'NO_CLOSETS')
        return render(request, 'error.html', {'obj': obj})
    mdf_closet_records = closet_records.filter(
        category__in=[Closet.CategoryChoices.MDF, Closet.CategoryChoices.MDF_IDF])
    if not mdf_closet_records:
        base_system.generate_error(obj, 'NO_MDF')
        return render(request, 'error.html', {'obj': obj})
    router_records = base_system.get_device_records(Router, mdf_closet_records)
    if not router_records and site_record.project_type == Site.ProjectTypeChoices.GREENFIELD:
        return redirect(reverse('wan_green', kwargs={'site_id': site_record.id}))
    return redirect(reverse('wan_brown', kwargs={'site_id': site_record.id}))
