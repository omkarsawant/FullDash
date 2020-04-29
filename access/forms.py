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
            'ap_count',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stack_model'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['style'] = 'width:1in'
        self.fields['mgig_count'].widget.attrs['style'] = 'width:1in'
        self.fields['ap_count'].widget.attrs['style'] = 'width:1in'
        mgig_count_choices = [
            (
                AccessSwitch.MgigSwitchCountChoices.MSC_0,
                AccessSwitch.MgigSwitchCountChoices.MSC_0.value
            )
        ]
        if kwargs['instance'].switch_count:
            for index in range(1, (kwargs['instance'].switch_count+1)):
                exec('mgig_count_choices.append((AccessSwitch.MgigSwitchCountChoices.MSC_' + str(
                    index) + ', AccessSwitch.MgigSwitchCountChoices.MSC_' + str(index) + '.value))')
        self.fields['mgig_count'].choices = mgig_count_choices


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

    def __init__(self, *args, access_switch, **kwargs):
        super().__init__(*args, **kwargs)
        vlan_records = Vlan.objects.filter(access_switch=access_switch)
        all_vlan_ids = vlan_records.values_list('vlan_id')
        voice_vlan_ids = vlan_records.filter(
            vlan_type=Vlan.VlanTypeChoices.VOICE).values_list('vlan_id')
        self.fields['access_vlan'].widget = forms.Select(
            choices=[(vlan_id, vlan_id) for vlan_id in all_vlan_ids])
        self.fields['voice_vlan'].widget = forms.Select(
            choices=[(vlan_id, vlan_id) for vlan_id in voice_vlan_ids])
        self.fields['access_vlan'].widget.attrs['style'] = 'width:1in'
        self.fields['voice_vlan'].widget.attrs['style'] = 'width:1in'


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
        self.fields['closet'].widget.attrs['style'] = 'width:1.5in'

    closet = forms.ModelChoiceField(
        queryset=Closet.objects.none(), empty_label=None)


class VlanCreateGreenForm(forms.ModelForm):
    class Meta:
        model = Vlan
        fields = [
            'vlan_type',
            'svi_mask_length',
            'vlan_id',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vlan_id'].widget.attrs.update(readonly=True)
        self.fields['vlan_id'].widget.attrs.update(placeholder='Autogen')
        self.fields['vlan_id'].widget.attrs['style'] = 'width:1in'
        self.fields['vlan_type'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['svi_mask_length'].widget.attrs['onchange'] = 'this.form.submit()'


class VlanCreateBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


VlanCreateGreenFormset = forms.modelformset_factory(
    Vlan, can_delete=True, extra=1, form=VlanCreateGreenForm, formset=VlanCreateBaseModelFormset)
