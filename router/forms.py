from django import forms
from .models import Router
from interactive import base_system


class WanBrownForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = [
            'loopback_cidr',
            'downlink_1_cidr',
            'downlink_2_cidr',
            'interlink_1_cidr',
            'interlink_2_cidr',
            'wan_type',
            'wan_provider',
            'access_id',
            'port_id',
            'access_bw',
            'port_bw',
            'wan_cidr',
            'local_asn',
            'remote_asn',
            'other_router_loopback_cidr',
            'isp_cidr',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: placeholders for all forms everywhere
        self.fields['loopback_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['downlink_1_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['downlink_2_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['interlink_1_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['interlink_2_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['wan_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']


class WanGreenForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = [
            'wan_type',
            'wan_provider',
            'access_id',
            'port_id',
            'access_bw',
            'port_bw',
            'wan_cidr',
            'local_asn',
            'remote_asn',
        ]

    def clean_remote_asn(self, *args, **kwargs):
        remote_asn = self.cleaned_data['remote_asn']
        if(remote_asn < 65000):
            # TODO: finish the code!
            raise forms.ValidationError('lolmax1')
        return remote_asn

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wan_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
