from django import forms
from .models import Overview


class OverviewCreateForm(forms.ModelForm):

    class Meta:
        model = Overview
        fields = [
            'project_type',
            'crest',
        ]

    def clean_crest(self, *args, **kwargs):
        crest = self.cleaned_data['crest']
        if (crest < 1000000) or (crest > 2000000):
            raise forms.ValidationError("Invalid CREST ID")
        return crest


class OverviewUpdateForm(forms.ModelForm):

    class Meta:
        model = Overview
        fields = [
            'project_type',
            'crest',
            'address',
            'capacity',
            'headcount',
            'nearest_dc',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].widget.attrs.update(readonly=True)
        self.fields['crest'].widget.attrs.update(readonly=True)
        self.fields['address'].widget.attrs.update(readonly=True)
        self.fields['capacity'].widget.attrs.update(readonly=True)
        self.fields['headcount'].widget.attrs.update(readonly=True)
