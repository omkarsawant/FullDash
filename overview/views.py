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
        self.submit_text = 'Lookup Site'
        self.template_name = 'create_update.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        form.submit_text = self.submit_text
        return render(request, self.template_name, {'form': form})


class OverviewUpdateView(UpdateView):
    def __init__(self, *args, **kwargs):
        self.form_class = OverviewUpdateForm
        self.queryset = Overview.objects.all()
        self.submit_text = 'Create Network'
        self.template_name = 'create_update.html'

    def get(self, request, *args, **kwargs):
        self.initial = self.get_site_details(model_to_dict(self.get_object()))
        form = self.form_class(initial=self.initial)
        form.submit_text = self.submit_text
        return render(request, self.template_name, {'form': form})

    def get_object(self):
        return get_object_or_404(Overview, id=self.kwargs.get('id'))

    def get_site_details(self, site):
        site['capacity'] = 915
        return site

    def get_success_url(self, *args, **kwargs):
        # return reverse('overview:list')
        return reverse('floors')
