from django import forms

from .models import ExcludedSubnet, Supernet
from interactive import base_system
from onboard.models import Site


class ExcludedSubnetCreateForm(forms.ModelForm):
    class Meta:
        model = ExcludedSubnet
        fields = [
            'subnet_cidr'
        ]


class ExcludedSubnetCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


ExcludedSubnetCreateFormset = forms.modelformset_factory(
    ExcludedSubnet, can_delete=True, extra=1, form=ExcludedSubnetCreateForm, formset=ExcludedSubnetCreateBaseModelFormset)


class NavbarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['site'].widget.attrs['class'] = 'selectpicker form-control form-control-dark'
        self.fields['site'].widget.attrs['data-live-search'] = 'true'

    site = forms.ModelChoiceField(queryset=Site.objects.values_list(
        'network_name', flat=True), empty_label=None)


class OverviewForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = [
            'network_name',
            'project_type',
            'capacity',
            'headcount',
            'network_type',
            'nearest_dc',
            'router',
            'core',
            'server',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_key in self.fields:
            self.fields[field_key].widget.attrs['disabled'] = True
        self.fields['network_name'].widget.attrs['size'] = 64


class SupernetCreateForm(forms.ModelForm):
    class Meta:
        model = Supernet
        fields = [
            'supernet_cidr',
        ]


class SupernetCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


SupernetCreateFormset = forms.modelformset_factory(
    Supernet, can_delete=True, extra=1, form=SupernetCreateForm, formset=SupernetCreateBaseModelFormset)
