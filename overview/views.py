from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Overview
from .forms import OverviewCreateForm, OverviewUpdateForm


def overview_create_view(request, *args, **kwargs):
    intial = None
    # initialization
    # form filling
    if request.method == 'POST':
        # initialization
        # form filling
        form = OverviewCreateForm(request.POST, initial=intial)
        if form.is_valid():
            model = form.save()
            print(dir(model))
            return redirect(reverse('overview_update', kwargs={'id': model.get('id')}))
            # redirect
        for error in form.errors.values():
            messages.error(request, error)
        return render(request, 'overview_create.html', {})
    # initialization
    # form filling
    form = OverviewCreateForm(initial=intial)
    return render(request, 'overview_create.html', {})


class OverviewCreateView(CreateView):
    def __init__(self, *args, **kwargs):
        self.form_class = OverviewCreateForm
        self.template_name = 'overview_create.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, initial=self.initial)
        if form.is_valid():
            return super().form_valid(form)
        for error in form.errors.values():
            messages.error(request, error)
        return render(request, self.template_name, {'form': form})


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
