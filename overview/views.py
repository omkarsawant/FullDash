from django.shortcuts import render
from django.views.generic import CreateView
from .models import Overview
from .forms import OverviewCreateForm


class OverviewCreateView(CreateView):
    template_name = 'create.html'
    form_class = OverviewCreateForm
    queryset = Overview.objects.all()
