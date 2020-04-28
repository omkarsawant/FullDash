from django import forms
from .models import Router
from interactive import base_system


class WanBrownForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = [
            'loopback_ip',
            'downlink_1_ip',
            'downlink_2_ip',
            'interlink_1_ip',
            'interlink_2_ip',
            'wan_type',
            'wan_provider',
            'access_id',
            'port_id',
            'access_bw',
            'port_bw',
            'wan_link_cidr',
            'local_asn',
            'remote_asn',
            'other_router_loopback_ip',
            'isp_ip',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: placeholders for all forms everywhere
        self.fields['loopback_ip'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['downlink_1_ip'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['downlink_2_ip'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['interlink_1_ip'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['interlink_2_ip'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
        self.fields['wan_link_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']


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
            'wan_link_cidr',
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
        self.fields['wan_link_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']
