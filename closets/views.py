from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView
from overview.models import Overview
from .models import Closets
from .forms import ClosetsCreateFormset


def closets_create_view(request, *args, **kwargs):
    obj = type('', (object,), {})()
    template_name = 'closets_create.html'
    overview_record = get_object_or_404(Overview, id=kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    if request.method == 'GET':
        obj.formset = ClosetsCreateFormset(queryset=closets_records)
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        obj.formset = ClosetsCreateFormset(
            request.POST, queryset=closets_records)
        instances = obj.formset.save(commit=False)
        for instance in instances:
            instance.overview = overview_record
            instance.save()
        for form in obj.formset.deleted_forms:
            form.save(commit=False).delete()
        return redirect(reverse('closets_create', kwargs={'id': kwargs['id']}))
