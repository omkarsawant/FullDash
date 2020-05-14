from django import forms
from ipaddress import IPv4Network

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wan_link_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']

    def clean_local_asn(self, *args, **kwargs):
        local_asn = self.cleaned_data['local_asn']
        if local_asn < 64512 or local_asn > 65534:
            raise forms.ValidationError(
                'Allowed values for ASNs are from 64512 to 65534 only')
        return local_asn

    def clean_remote_asn(self, *args, **kwargs):
        remote_asn = self.cleaned_data['remote_asn']
        if remote_asn < 64512 or remote_asn > 65534:
            raise forms.ValidationError(
                'Allowed values for ASNs are from 64512 to 65534 only')
        return remote_asn

    def clean_wan_link_cidr(self, *args, **kwargs):
        wan_link_cidr = self.cleaned_data['wan_link_cidr']
        try:
            wan_link_cidr_obj = IPv4Network(wan_link_cidr, False)
        except:
            raise forms.ValidationError('Invalid WAN IP address entered')
        return wan_link_cidr


class WanGreenSubForm(forms.ModelForm):
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
            'remote_asn',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wan_link_cidr'].widget.attrs['placeholder'] = base_system.PLACEHOLDERS['IP']

    def clean_remote_asn(self, *args, **kwargs):
        remote_asn = self.cleaned_data['remote_asn']
        if remote_asn < 64512 or remote_asn > 65534:
            raise forms.ValidationError(
                'Allowed values for ASNs are from 64512 to 65534 only')
        return remote_asn

    def clean_wan_link_cidr(self, *args, **kwargs):
        wan_link_cidr = self.cleaned_data['wan_link_cidr']
        try:
            wan_link_cidr_obj = IPv4Network(wan_link_cidr, False)
        except:
            raise forms.ValidationError('Invalid WAN IP address entered')
        return wan_link_cidr
