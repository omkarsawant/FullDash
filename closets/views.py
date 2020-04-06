from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView
from overview.models import Overview
from .models import Closets
from .forms import ClosetsCreateFormset


def closets_create_view(request, *args, **kwargs):
    intial = dict()
    obj = type('', (object,), {})()
    template_name = 'closets_create.html'
    overview_record = get_object_or_404(Overview, id=kwargs['id'])
    closets_records = Closets.objects.filter(overview=overview_record)
    obj.formset = ClosetsCreateFormset(queryset=closets_records)
    # form filling
    if request.method == 'GET':
        # initialization
        # form filling
        obj.form = OverviewCreateForm(initial=intial)
        return render(request, template_name, {'obj': obj})
    if request.method == 'POST':
        # initialization
        # form filling
        obj.form = OverviewCreateForm(request.POST, initial=intial)
        if obj.form.is_valid():
            model = obj.form.save()
            return redirect(reverse('url_name', kwargs={}))
        for error in obj.form.errors.values():
            messages.error(request, error)
        return render(request, template_name, {'obj': obj})


class ClosetsCreateView(CreateView):
    def __init__(self, *args, **kwargs):
        self.form_class = ClosetsCreateFormset
        self.template_name = 'closets_create.html'

    def form_valid(self, formset):
        instances = formset.save(commit=False)
        overview_object = get_object_or_404(
            Overview, id=self.kwargs.get('id'))
        for instance in instances:
            instance.overview = overview_object
            instance.save()
        for form in formset.deleted_forms:
            form.save(commit=False).delete()
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        overview_object = get_object_or_404(
            Overview, id=self.kwargs.get('id'))
        previous_closets = Closets.objects.filter(overview=overview_object)
        formset = self.form_class(queryset=previous_closets)
        return render(request, self.template_name, {'formset': formset})

    def get_success_url(self):
        return reverse('closets_create', kwargs={'id': self.kwargs.get('id')})
