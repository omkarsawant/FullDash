from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ExcludedSubnetCreateFormset, OverviewForm, SupernetCreateFormset
from .models import ExcludedSubnet, Supernet
from interactive import base_system
from onboard.models import Site


def overview_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'overview.html'
    site_record = base_system.initialize_navbar(obj, request, kwargs['id'])
    supernet_records = Supernet.objects.filter(site=site_record)
    excluded_subnet_records = ExcludedSubnet.objects.filter(site=site_record)
    if request.method == 'GET':
        obj.overview_form = OverviewForm(
            instance=site_record, prefix='overview')
        obj.supernet_formset = SupernetCreateFormset(
            queryset=supernet_records, prefix='supernet')
        obj.excluded_subnet_formset = ExcludedSubnetCreateFormset(
            queryset=excluded_subnet_records, prefix='excluded_subnet')
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'id': site_record_navbar.id}))
        obj.overview_form = OverviewForm(
            instance=site_record, prefix='overview')
        obj.supernet_formset = SupernetCreateFormset(
            request.POST, queryset=supernet_records, prefix='supernet')
        obj.excluded_subnet_formset = ExcludedSubnetCreateFormset(
            request.POST, queryset=excluded_subnet_records, prefix='excluded_subnet')
        if obj.supernet_formset.is_valid() and obj.excluded_subnet_formset.is_valid():
            supernet_instances = obj.supernet_formset.save(commit=False)
            for supernet_instance in supernet_instances:
                supernet_instance.site = site_record
                supernet_instance.save()
            for supernet_form in obj.supernet_formset.deleted_forms:
                supernet_form.save(commit=False).delete()
            excluded_subnet_instances = obj.excluded_subnet_formset.save(
                commit=False)
            for excluded_subnet_instance in excluded_subnet_instances:
                excluded_subnet_instance.site = site_record
                excluded_subnet_instance.save()
            for excluded_subnet_form in obj.excluded_subnet_formset.deleted_forms:
                excluded_subnet_form.save(commit=False).delete()
            return redirect(reverse('overview', kwargs={'id': kwargs['id']}))
        base_system.set_formset_errors(
            request, obj.supernet_formset, obj.excluded_subnet_formset)
        return render(request, template_name, {'obj': obj})
