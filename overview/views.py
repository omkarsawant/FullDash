from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, UpdateView
from .models import Overview
from .forms import OverviewCreateForm, OverviewUpdateForm


class OverviewCreateView(CreateView):
    def __init__(self, *args, **kwargs):
        self.form_class = OverviewCreateForm
        self.template_name = 'overview_create.html'


class OverviewUpdateView(UpdateView):
    def __init__(self, *args, **kwargs):
        self.form_class = OverviewUpdateForm
        self.queryset = Overview.objects.all()
        self.template_name = 'overview_update.html'

    def get(self, request, *args, **kwargs):
        self.initial = self.get_site_details(model_to_dict(self.get_object()))
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def get_object(self):
        return get_object_or_404(Overview, id=self.kwargs.get('id'))

    def get_site_details(self, site):
        site['capacity'] = 915
        return site

    def get_success_url(self, *args, **kwargs):
        # return reverse('overview:list')
        return reverse('closets_create', kwargs={'id': self.kwargs.get('id')})
