from django import forms

from . import base_access
from .models import AccessSwitch, AccessPortBlock, Vlan

from closet.models import Closet
from interactive import base_system


class AccessSwitchBrownForm(forms.ModelForm):
    class Meta:
        model = AccessSwitch
        fields = [
            'stack_model',
            'switch_count',
            'mgig_count',
            'loopback_ip',
            'uplink_1_ip',
            'uplink_2_ip',
            'ap_count',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stack_model'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['switch_count'].widget.attrs['style'] = 'width:1in'
        self.fields['mgig_count'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['mgig_count'].widget.attrs['style'] = 'width:1in'
        self.fields['ap_count'].widget.attrs['style'] = 'width:1in'
        mgig_count_choices = []
        if kwargs['instance'].switch_count:
            for index in range(kwargs['instance'].switch_count+1):
                exec('mgig_count_choices.append((AccessSwitch.MgigSwitchCountChoices.MSC_' + str(
                    index) + ', AccessSwitch.MgigSwitchCountChoices.MSC_' + str(index) + '.value))')
        self.fields['mgig_count'].choices = mgig_count_choices


class AccessSwitchGreenForm(forms.ModelForm):
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
        self.fields['mgig_count'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['mgig_count'].widget.attrs['style'] = 'width:1in'
        self.fields['ap_count'].widget.attrs['style'] = 'width:1in'
        mgig_count_choices = []
        if kwargs['instance'].switch_count:
            for index in range(kwargs['instance'].switch_count+1):
                exec('mgig_count_choices.append((AccessSwitch.MgigSwitchCountChoices.MSC_' + str(
                    index) + ', AccessSwitch.MgigSwitchCountChoices.MSC_' + str(index) + '.value))')
        self.fields['mgig_count'].choices = mgig_count_choices


class AccessPortBlockForm(forms.ModelForm):
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
        self.access_switch = kwargs.pop('access_switch', None)
        super().__init__(*args, **kwargs)
        if not self.access_switch:
            return
        vlan_records = Vlan.objects.filter(
            access_switch=self.access_switch)
        all_vlan_ids = vlan_records.values_list('vlan_id')
        voice_vlan_ids = vlan_records.filter(
            vlan_type=Vlan.VlanTypeChoices.VOICE).values_list('vlan_id')
        if all_vlan_ids and all_vlan_ids[0][0]:
            self.fields['access_vlan'].widget = forms.Select(
                choices=[(vlan_id_tuple[0], vlan_id_tuple[0])
                         for vlan_id_tuple in all_vlan_ids])
        if voice_vlan_ids and voice_vlan_ids[0][0]:
            self.fields['voice_vlan'].widget = forms.Select(
                choices=[(vlan_id_tuple[0], vlan_id_tuple[0])
                         for vlan_id_tuple in voice_vlan_ids])
        if self.access_switch.stack_model and self.access_switch.switch_count:
            self.fields['start_intr'].widget = forms.Select(
                choices=base_access.get_stack_port_names(self.access_switch))
            self.fields['end_intr'].widget = forms.Select(
                choices=base_access.get_stack_port_names(self.access_switch))
        self.fields['access_vlan'].widget.attrs['style'] = 'width:1in'
        self.fields['voice_vlan'].widget.attrs['style'] = 'width:1in'
        self.fields['start_intr'].widget.attrs['class'] = 'selectpicker'
        self.fields['start_intr'].widget.attrs['data-live-search'] = 'true'
        self.fields['start_intr'].widget.attrs['data-width'] = '2in'
        self.fields['start_intr'].widget.attrs['data-size'] = 4
        self.fields['start_intr'].widget.attrs['data-style'] = 'btn-outline-light border-dark text-dark rounded-0'
        self.fields['end_intr'].widget.attrs['class'] = 'selectpicker'
        self.fields['end_intr'].widget.attrs['data-live-search'] = 'true'
        self.fields['end_intr'].widget.attrs['data-width'] = '2in'
        self.fields['end_intr'].widget.attrs['data-size'] = 4
        self.fields['end_intr'].widget.attrs['data-style'] = 'btn-outline-light border-dark text-dark rounded-0'


class AccessPortBlockBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


AccessPortBlockFormSet = forms.modelformset_factory(
    AccessPortBlock, can_delete=True, extra=1, form=AccessPortBlockForm, formset=AccessPortBlockBaseModelFormset)


class AccessListingForm(forms.Form):
    def __init__(self, *args, site_record, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['closet'].queryset = Closet.objects.filter(
            site=site_record).values_list('closet', flat=True)
        self.fields['closet'].widget.attrs['style'] = 'width:1.5in'

    closet = forms.ModelChoiceField(
        queryset=Closet.objects.none(), empty_label=None)


class VlanBrownForm(forms.ModelForm):
    class Meta:
        model = Vlan
        fields = [
            'vlan_type',
            'vlan_id',
            'name',
            'svi_ip',
            'svi_mask_length',
        ]

    def __init__(self, *args, **kwargs):
        self.access_switch = kwargs.pop('access_switch', None)
        super().__init__(*args, **kwargs)
        self.fields['vlan_type'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['vlan_id'].widget.attrs['style'] = 'width:0.5in'
        self.fields['name'].widget.attrs['style'] = 'width:1.75in'
        self.fields['svi_ip'].widget.attrs['style'] = 'width:1.5in'
        self.fields['svi_mask_length'].widget.attrs['onchange'] = 'this.form.submit()'


class VlanGreenForm(forms.ModelForm):
    class Meta:
        model = Vlan
        fields = [
            'vlan_type',
            'svi_mask_length',
            'vlan_id',
        ]

    def __init__(self, *args, **kwargs):
        self.access_switch = kwargs.pop('access_switch', None)
        super().__init__(*args, **kwargs)
        self.fields['vlan_id'].widget.attrs.update(readonly=True)
        self.fields['vlan_id'].widget.attrs.update(placeholder='Autogen')
        self.fields['vlan_id'].widget.attrs['style'] = 'width:1in'
        self.fields['vlan_type'].widget.attrs['onchange'] = 'this.form.submit()'
        self.fields['svi_mask_length'].widget.attrs['onchange'] = 'this.form.submit()'


class VlanBaseModelFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def _should_delete_form(self, form):
        form.full_clean()
        return super()._should_delete_form(form)


VlanBrownFormset = forms.modelformset_factory(
    Vlan, can_delete=True, extra=1, form=VlanBrownForm, formset=VlanBaseModelFormset)

VlanGreenFormset = forms.modelformset_factory(
    Vlan, can_delete=True, extra=1, form=VlanGreenForm, formset=VlanBaseModelFormset)
