from django import forms

from .models import AccessSwitch, AccessPortBlock, Vlan

from closet.models import Closet


class AccessSwitchCreateGreenForm(forms.ModelForm):
    class Meta:
        model = AccessSwitch
        fields = [
            'stack_model',
            'switch_count',
            'mgig_count',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stack_model'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['style'] = "width:0.5in"
        self.fields['mgig_count'].widget.attrs['style'] = "width:0.5in"
        if kwargs['instance'].switch_count:
            self.fields['mgig_count'].widget.choices = [
                (index, index) for index in range(1, (kwargs['instance'].switch_count+1))]


class AccessPortBlockCreateGreenForm(forms.ModelForm):
    class Meta:
        model = AccessPortBlock
        fields = [
            'start_intr',
            'end_intr',
            'access_vlan',
            'voice_vlan',
            'legacy_qos',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_key in self.fields:
            self.fields[field_key].widget.attrs['onchange'] = 'this.form.submit()'


class AccessPortBlockCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


AccessPortBlockCreateGreenFormSet = forms.modelformset_factory(
    AccessPortBlock, can_delete=True, extra=1, form=AccessPortBlockCreateGreenForm, formset=AccessPortBlockCreateBaseModelFormset)


class AccessListingForm(forms.Form):
    def __init__(self, *args, site_record, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['closet'].queryset = Closet.objects.filter(
            site=site_record).values_list('closet', flat=True)
        self.fields['closet'].widget.attrs['style'] = "width:1.5in"

    closet = forms.ModelChoiceField(
        queryset=Closet.objects.none(), empty_label=None)


class VlanCreateGreenForm(forms.ModelForm):
    class Meta:
        model = Vlan
        fields = [
            'vlan_type',
            'svi_mask_length',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_key in self.fields:
            self.fields[field_key].widget.attrs['onchange'] = 'this.form.submit()'


class VlanCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


VlanCreateGreenFormset = forms.modelformset_factory(
    Vlan, can_delete=True, extra=1, form=VlanCreateGreenForm, formset=VlanCreateBaseModelFormset)
