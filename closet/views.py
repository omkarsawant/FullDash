from django.shortcuts import redirect, render
from django.urls import reverse
from interactive import base_system
from onboard.models import Site
from .models import Closet
from .forms import ClosetCreateFormset


def closet_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'closet_create.html'
    site_record = base_system.initialize_navbar(obj, request, kwargs['id'])
    closet_records = Closet.objects.filter(site=site_record)
    if request.method == 'GET':
        obj.formset = ClosetCreateFormset(queryset=closet_records)
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        if 'navbar' in request.POST:
            site_record_navbar = Site.objects.get(
                network_name=request.POST['site'])
            return redirect(reverse('overview', kwargs={'id': site_record_navbar.id}))
        obj.formset = ClosetCreateFormset(request.POST)
        if obj.formset.is_valid():
            instances = obj.formset.save(commit=False)
            for instance in instances:
                if not instance.closet:
                    instance.site = site_record
                    closet_record_index = len(Closet.objects.filter(
                        site=site_record, floor=instance.floor))
                    closet_record_number = (closet_record_index % 26) + 1
                    instance.closet = f'{instance.floor:03}{chr(closet_record_number+96)}'
                instance.save()
            for form in obj.formset.deleted_forms:
                # TODO: change closet numbers
                form.save(commit=False).delete()
            return redirect(reverse('closets', kwargs={'id': kwargs['id']}))
        base_system.set_formset_errors(request, obj.formset)
        return render(request, template_name, {'obj': obj})
