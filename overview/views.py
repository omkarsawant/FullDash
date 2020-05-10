from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import smart_str
from os import remove

from .forms import BuildForm, ExcludedSubnetCreateFormset, OverviewForm, SupernetCreateFormset
from .models import ExcludedSubnet, Supernet
from interactive import base_system, generate_docs
from onboard.models import Site
from interactive.settings import BASE_DIR


def build_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'build.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    if request.method == 'GET':
        obj.build_form = BuildForm()
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.build_form = BuildForm(request.POST)
        if 'subnet' in request.POST:
            build_output = generate_docs.generate_docs(site_record, 'subnet')
        elif 'diagram' in request.POST:
            if obj.build_form.is_valid():
                build_output = generate_docs.generate_docs(
                    site_record, 'diagram', diagram_author=obj.build_form.cleaned_data['diagram_author'])
            else:
                base_system.set_form_errors(request, obj.build_form)
                return render(request, template_name, {'obj': obj})
        elif 'config' in request.POST:
            build_output = generate_docs.generate_docs(site_record, 'config')
        elif 'all' in request.POST:
            if obj.build_form.is_valid():
                build_output = generate_docs.generate_docs(
                    site_record, 'all', diagram_author=obj.build_form.cleaned_data['diagram_author'])
            else:
                base_system.set_form_errors(request, obj.build_form)
                return render(request, template_name, {'obj': obj})
        obj.build_form = BuildForm(request.POST, initial={
                                   'build_output': build_output})
        gda_zip_filename = BASE_DIR + \
            base_system.DIRECTORIES['staging'] + \
            base_system.get_filename(site_record.crest, 'zip')
        gda_zip_file = open(gda_zip_filename, 'rb')
        http_response = HttpResponse(
            gda_zip_file.read(), content_type='application/zip')
        http_response['Content-Disposition'] = 'attachment; filename="foo.zip"'
        gda_zip_file.close()
        remove(gda_zip_filename)
        return http_response
        # return render(request, template_name, {'obj': obj})


def overview_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'overview.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
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
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
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
            return redirect(reverse('overview', kwargs={'site_id': site_record.id}))
        base_system.set_formset_errors(
            request, obj.supernet_formset, obj.excluded_subnet_formset)
        return render(request, template_name, {'obj': obj})
