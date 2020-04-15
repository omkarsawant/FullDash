from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from interactive import base_system
from .models import Overview
from .forms import Navbar, OverviewCreateForm, OverviewUpdateForm


def overview_create_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    if request.method == 'GET':
        obj.form = OverviewCreateForm(initial=initial)
        return render(request, 'overview_create.html', {'obj': obj})
    if request.method == 'POST':
        obj.form = OverviewCreateForm(request.POST, initial=initial)
        if obj.form.is_valid():
            model = obj.form.save()
            return redirect(reverse('overview_update', kwargs={'id': model.id}))
        for error in obj.form.errors.values():
            messages.error(request, error)
        return render(request, 'overview_create.html', {'obj': obj})


def overview_update_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'overview_update.html'
    overview_record = base_system.initialize_navbar(obj, kwargs['id'])
    initial.update(model_to_dict(overview_record))
    if request.method == 'GET':
        if not overview_record.capacity:
            site_details = base_system.get_site_details(overview_record.crest)
            for site_detail in site_details:
                initial[site_detail] = site_details[site_detail]
                exec('overview_record.' + site_detail +
                     ' = site_details[site_detail]')
            overview_record.save()
        obj.form = OverviewUpdateForm(initial=initial)
        obj.submit_type = 'btn-outline-primary'
        obj.submit_text = 'Create Network'
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        obj.form = OverviewUpdateForm(request.POST, instance=overview_record)
        if obj.form.is_valid():
            site_details = base_system.get_site_details(overview_record.crest)
            meeting_standards = True
            for site_detail in site_details:
                print(str(request.POST[site_detail]))
                print(str(site_details[site_detail]))
                if str(request.POST[site_detail]) != str(site_details[site_detail]):
                    meeting_standards = False
                    break
            if not meeting_standards:
                if overview_record.exception_confirmed is None:
                    overview_record.exception_confirmed = False
                    base_system.activate_modal(obj, 'Issue', 'Issue!')
                    obj.submit_type = 'btn-outline-warning'
                    obj.submit_text = 'Confirm Non-Standard Network'
                    overview_record.save()
                    return render(request, template_name, {'obj': obj})
                elif overview_record.exception_confirmed is False:
                    overview_record.exception_confirmed = True
            obj.form.save()
            return redirect(reverse('closets_create', kwargs={'id': kwargs['id']}))
        for error in obj.form.errors.values():
            messages.error(request, error)
        return render(request, template_name, {'obj': obj})
