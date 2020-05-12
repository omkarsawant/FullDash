from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import OnboardLookupForm, OnboardDetailForm
from onboard.models import Site
from interactive import base_system


def onboarding_view(request, *args, **kwargs):
    initial = dict()
    obj = type('', (object,), {})()
    template_name = 'onboard.html'
    site_record = base_system.initialize_navbar(obj, request)
    if request.method == 'GET':
        obj.form = OnboardLookupForm()
        obj.submit_type = 'btn-outline-primary'
        obj.submit_text = 'Create Network'
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        if 'capacity' in request.POST:
            obj.form = OnboardDetailForm(request.POST)
            if obj.form.is_valid():
                cleaned_data = obj.form.cleaned_data
                meeting_standards = base_system.check_hardware_standards(
                    request, cleaned_data['crest'])
                illegal_standards = base_system.check_illegal_configuration(
                    request)
                if (not meeting_standards) and (illegal_standards):
                    base_system.set_error(
                        request, 'illegal_site', illegal_standards)
                    obj.submit_type = 'btn-outline-primary'
                    obj.submit_text = 'Create Network'
                    return render(request, template_name, {'obj': obj})
                if (not meeting_standards) and ('confirm' not in request.POST):
                    base_system.activate_modal(obj, 'NON_STANDARD')
                    obj.submit_type = 'btn-outline-warning'
                    obj.submit_name = 'confirm'
                    obj.submit_text = 'Confirm Non-Standard Network'
                    return render(request, template_name, {'obj': obj})
                site_record = obj.form.save(commit=False)
                site_record_number = len(
                    Site.objects.filter(crest=site_record.crest)) + 1
                site_record.network_name = f'{site_record.crest}--{site_record.address}--{site_record_number:03}'
                site_record.signal_onboarded_site = True
                site_record.signal_present_core = False if site_record.core == Site.CoreChoices.NO_CORE else True
                site_record.signal_present_server = False if site_record.server == Site.ServerChoices.NO_SERVER else True
                site_record.save()
                return redirect(reverse('closets', kwargs={'site_id': site_record.id}))
            base_system.set_form_errors(request, obj.form)
            return render(request, template_name, {'obj': obj})
        else:
            obj.form = OnboardLookupForm(request.POST)
            if obj.form.is_valid():
                initial.update(obj.form.cleaned_data)
                site_details = base_system.get_site_details(initial['crest'])
                if site_details:
                    initial.update(site_details)
                    obj.form = OnboardDetailForm(initial=initial)
                    obj.submit_type = 'btn-outline-primary'
                    obj.submit_text = 'Create Network'
                    return render(request, template_name, {'obj': obj})
                else:
                    base_system.set_error(request, 'no_site')
            base_system.set_form_errors(request, obj.form)
            obj.submit_type = 'btn-outline-primary'
            obj.submit_text = 'Create Network'
            return render(request, template_name, {'obj': obj})
