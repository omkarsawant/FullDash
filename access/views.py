from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from closet.models import Closet
from interactive import base_system
from onboard.models import Site

from .forms import AccessSwitchCreateGreenForm, AccessPortBlockCreateGreenFormSet, AccessListingForm, VlanCreateGreenFormset
from .models import AccessSwitch


def access_brown_view(request, *args, **kwargs):
    pass


def access_green_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'access_green.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    obj.access_switch_record = AccessSwitch.objects.filter(
        id=kwargs['access_switch_id'])
    if request.method == 'GET':
        obj.access_switch_form = AccessSwitchCreateGreenForm(
            instance=obj.access_switch_record[0], prefix='access_switch')
        obj.vlan_formset = VlanCreateGreenFormset(
            queryset=obj.access_switch_record, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockCreateGreenFormSet(
            queryset=obj.access_switch_record, prefix='access_port_block')
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.access_switch_form = AccessSwitchCreateGreenForm(
            request.POST, instance=obj.access_switch_record[0], prefix='access_switch')
        obj.vlan_formset = VlanCreateGreenFormset(
            request.POST, queryset=obj.access_switch_record, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockCreateGreenFormSet(
            request.POST, queryset=obj.access_switch_record, prefix='access_port_block')
        if obj.access_switch_form.is_valid():
            print(obj.access_switch_form.cleaned_data)
            obj.access_switch_form.save()
        if obj.vlan_formset.is_valid():
            vlan_instances = obj.vlan_formset.save(commit=False)
            for vlan_instance in vlan_instances:
                vlan_instance.site = site_record
                vlan_instance.save()
            for vlan_form in obj.vlan_formset.deleted_forms:
                vlan_form.save(commit=False).delete()
        if obj.access_port_block_formset.is_valid():
            access_port_block_instances = obj.access_port_block_formset.save(
                commit=False)
            for access_port_block_instance in access_port_block_instances:
                access_port_block_instance.site = site_record
                access_port_block_instance.save()
            for access_port_block_form in obj.access_port_block_formset.deleted_forms:
                access_port_block_form.save(commit=False).delete()
        if 'finish' in request.POST:
            return redirect(reverse('access_lising', kwargs={'site_id': site_record.id}))
        return redirect(reverse('access_green', kwargs={'site_id': site_record.id, 'access_switch_id': obj.access_switch_record[0].id}))


def access_listing_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'access_listing.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    if request.method == 'GET':
        closet_records = Closet.objects.filter(site=site_record)
        obj.access_switch_records = AccessSwitch.objects.filter(
            closet__in=closet_records)
        obj.form = AccessListingForm(site_record=site_record)
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        closet_record = Closet.objects.get(closet=request.POST['closet'])
        access_hostname = base_system.get_device_hostname(
            site_record, closet_record, AccessSwitch)
        access_switch_record = AccessSwitch.objects.create(
            hostname=access_hostname, closet=closet_record)
        if site_record.project_type == Site.ProjectTypeChoices.GREENFIELD:
            return redirect(reverse('access_green', kwargs={'site_id': site_record.id, 'access_switch_id': access_switch_record.id}))
        else:
            return redirect(reverse('access_brown', kwargs={'site_id': site_record.id, 'access_switch_id': access_switch_record.id}))
