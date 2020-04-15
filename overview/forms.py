from django import forms
from .models import Overview


class Navbar(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'selectpicker form-control form-control-dark'
            visible.field.widget.attrs['data-live-search'] = 'true'

    site = forms.ModelChoiceField(queryset=Overview.objects.values_list(
        'crest', flat=True), empty_label=None)


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
            'crest',
            'project_type',
            'address',
            'capacity',
            'headcount',
            'nearest_dc',
            'router',
            'core',
            'server',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].widget.attrs.update(readonly=True)
        self.fields['crest'].widget.attrs.update(readonly=True)
        self.fields['address'].widget.attrs.update(readonly=True)
        self.fields['capacity'].widget.attrs.update(readonly=True)
        self.fields['headcount'].widget.attrs.update(readonly=True)
