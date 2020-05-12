from django.shortcuts import redirect, render
from django.urls import reverse
from interactive import base_system
from onboard.models import Site
from access.models import AccessSwitch
from router.models import Router
from .models import Closet
from .forms import ClosetCreateFormset


def closet_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'closet_create.html'
    site_record = base_system.initialize_navbar(
        obj, request, kwargs['site_id'])
    closet_records = Closet.objects.filter(site=site_record)
    if request.method == 'GET':
        obj.formset = ClosetCreateFormset(queryset=closet_records)
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'site_id': site_record_navbar.id}))
        obj.formset = ClosetCreateFormset(request.POST)
        if obj.formset.is_valid():
            instances = obj.formset.save(commit=False)
            mdf_categories = [Closet.CategoryChoices.MDF,
                              Closet.CategoryChoices.MDF_IDF]
            idf_categories = [Closet.CategoryChoices.IDF,
                              Closet.CategoryChoices.MDF_IDF]
            for instance in instances:
                if instance.category in mdf_categories:
                    if len(Closet.objects.filter(site=site_record, category__in=mdf_categories)) > 1:
                        base_system.set_error(request, 'mdf_limit_exceeded')
                        continue
                if site_record.router == Site.RouterChoices.ISR_4331 and instance.category in idf_categories:
                    if len(Closet.objects.filter(site=site_record, category__in=idf_categories)) > 0:
                        base_system.set_error(
                            request, '4331_idf_limit_exceeded')
                        continue
                if site_record.router == Site.RouterChoices.ISR_4351 and instance.category in idf_categories:
                    if site_record.core == Site.CoreChoices.NO_CORE and len(Closet.objects.filter(site=site_record, category__in=idf_categories)) > 1:
                        base_system.set_error(
                            request, '4351_idf_limit_exceeded')
                        continue
                if not instance.closet:
                    instance.site = site_record
                    closet_record_index = len(Closet.objects.filter(
                        site=site_record, floor=instance.floor))
                    closet_record_number = (closet_record_index % 26) + 1
                    instance.closet = f'{instance.floor:03}{chr(closet_record_number+96)}'
                instance.save()
            for form in obj.formset.deleted_forms:
                closet_floor = form.cleaned_data['floor']
                form.save(commit=False).delete()
                remaining_closet_records = Closet.objects.filter(
                    site=site_record, floor=closet_floor)
                closet_record_index = 0
                for remaining_closet_record in remaining_closet_records:
                    closet_record_number = (closet_record_index % 26) + 1
                    remaining_closet_record.closet = f'{closet_floor:03}{chr(closet_record_number+96)}'
                    closet_record_index = closet_record_index+1
                    remaining_closet_record.save()
                    base_system.adjust_hostnames(
                        Router, remaining_closet_record)
                    base_system.adjust_hostnames(
                        AccessSwitch, remaining_closet_record)
            base_system.delete_extra_devices(AccessSwitch, Closet.objects.filter(
                site=site_record, category__in=[Closet.CategoryChoices.MDF]))
            base_system.delete_extra_devices(Router, Closet.objects.filter(
                site=site_record, category__in=[Closet.CategoryChoices.IDF]))
            # TODO: delete cores and servers also
            return redirect(reverse('closets', kwargs={'site_id': site_record.id}))
        base_system.set_formset_errors(request, obj.formset)
        return render(request, template_name, {'obj': obj})
