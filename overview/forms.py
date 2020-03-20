from django import forms
from .models import Overview


class OverviewCreateForm(forms.ModelForm):
    class Meta:
        model = Overview
        fields = [
            'crest'
        ]
