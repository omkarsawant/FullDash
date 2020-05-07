from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from closet.models import Closet
from interactive import base_system
from onboard.models import Site

from . import base_access
from .forms import AccessSwitchBrownForm, AccessSwitchGreenForm, AccessPortBlockFormSet, AccessListingForm, VlanBrownFormset, VlanGreenFormset
from .models import AccessSwitch, AccessPortBlock, Vlan


def access_brown_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'access_brown.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    obj.access_switch_record = AccessSwitch.objects.get(
        id=kwargs['access_switch_id'])
    vlan_records = Vlan.objects.filter(access_switch=obj.access_switch_record)
    access_port_block_records = AccessPortBlock.objects.filter(
        access_switch=obj.access_switch_record)
    if request.method == 'GET':
        obj.access_switch_form = AccessSwitchBrownForm(
            instance=obj.access_switch_record, prefix='access_switch')
        obj.vlan_formset = VlanBrownFormset(
            queryset=vlan_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockFormSet(
            queryset=access_port_block_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='access_port_block')
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.access_switch_form = AccessSwitchBrownForm(
            request.POST, instance=obj.access_switch_record, prefix='access_switch')
        obj.vlan_formset = VlanBrownFormset(
            request.POST, queryset=vlan_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockFormSet(
            request.POST, queryset=access_port_block_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='access_port_block')
        if obj.access_switch_form.is_valid():
            obj.access_switch_form.save()
        if obj.vlan_formset.is_valid():
            vlan_instances = obj.vlan_formset.save(commit=False)
            for vlan_instance in vlan_instances:
                vlan_instance.access_switch = obj.access_switch_record
                vlan_instance_valid, vlan_instance.vlan_id, vlan_instance.name = base_access.get_vlan_id(
                    site_record, vlan_instance)
                if vlan_instance_valid:
                    vlan_instance.save()
                else:
                    vlan_instance.delete()
            for vlan_form in obj.vlan_formset.deleted_forms:
                vlan_form.save(commit=False).delete()
        if obj.access_port_block_formset.is_valid():
            access_port_block_instances = obj.access_port_block_formset.save(
                commit=False)
            for access_port_block_instance in access_port_block_instances:
                access_port_block_instance.access_switch = obj.access_switch_record
                access_port_block_instance.save()
            for access_port_block_form in obj.access_port_block_formset.deleted_forms:
                access_port_block_form.save(commit=False).delete()
            access_switch_ports = base_access.get_stack_port_names(
                obj.access_switch_record)
            access_port_block_starts = []
            access_port_block_ends = []
            for access_port_block_record in AccessPortBlock.objects.filter(access_switch=obj.access_switch_record):
                access_port_block_start = access_switch_ports.index(
                    (access_port_block_record.start_intr,)*2)
                access_port_block_end = access_switch_ports.index(
                    (access_port_block_record.end_intr,)*2)
                for index in range(len(access_port_block_starts)):
                    if access_port_block_start >= access_port_block_starts[index] and access_port_block_start <= access_port_block_ends[index]:
                        site_record.signal_overlapping_access = True
                        site_record.save()
                        break
                if site_record.signal_overlapping_access:
                    break
                access_port_block_starts.append(access_port_block_start)
                access_port_block_ends.append(access_port_block_end)
        if 'finish' in request.POST:
            return redirect(reverse('access_lising', kwargs={'site_id': site_record.id}))
        return redirect(reverse('access_brown', kwargs={'site_id': site_record.id, 'access_switch_id': obj.access_switch_record.id}))


def access_green_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'access_green.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    obj.access_switch_record = AccessSwitch.objects.get(
        id=kwargs['access_switch_id'])
    vlan_records = Vlan.objects.filter(access_switch=obj.access_switch_record)
    access_port_block_records = AccessPortBlock.objects.filter(
        access_switch=obj.access_switch_record)
    if request.method == 'GET':
        obj.access_switch_form = AccessSwitchGreenForm(
            instance=obj.access_switch_record, prefix='access_switch')
        obj.vlan_formset = VlanGreenFormset(
            queryset=vlan_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockFormSet(
            queryset=access_port_block_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='access_port_block')
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.access_switch_form = AccessSwitchGreenForm(
            request.POST, instance=obj.access_switch_record, prefix='access_switch')
        obj.vlan_formset = VlanGreenFormset(
            request.POST, queryset=vlan_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='vlan')
        obj.access_port_block_formset = AccessPortBlockFormSet(
            request.POST, queryset=access_port_block_records, form_kwargs={'access_switch': obj.access_switch_record}, prefix='access_port_block')
        if obj.access_switch_form.is_valid():
            obj.access_switch_form.save()
        if obj.vlan_formset.is_valid():
            vlan_instances = obj.vlan_formset.save(commit=False)
            for vlan_instance in vlan_instances:
                vlan_instance.access_switch = obj.access_switch_record
                vlan_instance_valid, vlan_instance.vlan_id, vlan_instance.name = base_access.get_vlan_id(
                    site_record, vlan_instance)
                if vlan_instance_valid:
                    vlan_instance.save()
                else:
                    vlan_instance.delete()
            for vlan_form in obj.vlan_formset.deleted_forms:
                vlan_form.save(commit=False).delete()
        if obj.access_port_block_formset.is_valid():
            access_port_block_instances = obj.access_port_block_formset.save(
                commit=False)
            for access_port_block_instance in access_port_block_instances:
                access_port_block_instance.access_switch = obj.access_switch_record
                access_port_block_instance.save()
            for access_port_block_form in obj.access_port_block_formset.deleted_forms:
                access_port_block_form.save(commit=False).delete()
            access_switch_ports = base_access.get_stack_port_names(
                obj.access_switch_record)
            access_port_block_starts = []
            access_port_block_ends = []
            for access_port_block_record in AccessPortBlock.objects.filter(access_switch=obj.access_switch_record):
                access_port_block_start = access_switch_ports.index(
                    (access_port_block_record.start_intr,)*2)
                access_port_block_end = access_switch_ports.index(
                    (access_port_block_record.end_intr,)*2)
                for index in range(len(access_port_block_starts)):
                    if access_port_block_start >= access_port_block_starts[index] and access_port_block_start <= access_port_block_ends[index]:
                        site_record.signal_overlapping_access = True
                        site_record.save()
                        break
                if site_record.signal_overlapping_access:
                    break
                access_port_block_starts.append(access_port_block_start)
                access_port_block_ends.append(access_port_block_end)
        if 'finish' in request.POST:
            return redirect(reverse('access_lising', kwargs={'site_id': site_record.id}))
        return redirect(reverse('access_green', kwargs={'site_id': site_record.id, 'access_switch_id': obj.access_switch_record.id}))


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
        closet_record = Closet.objects.get(
            site=site_record, closet=request.POST['closet'])
        access_hostname = base_system.get_device_hostname(
            site_record, closet_record, AccessSwitch)
        access_switch_record = AccessSwitch.objects.create(
            hostname=access_hostname, closet=closet_record)
        if site_record.project_type == Site.ProjectTypeChoices.GREENFIELD:
            return redirect(reverse('access_green', kwargs={'site_id': site_record.id, 'access_switch_id': access_switch_record.id}))
        else:
            return redirect(reverse('access_brown', kwargs={'site_id': site_record.id, 'access_switch_id': access_switch_record.id}))
