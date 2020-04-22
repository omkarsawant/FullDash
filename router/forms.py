from django import forms
from .models import Router


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
            'wan_ip',
            'local_asn',
            'remote_asn',
            'other_router_loopback',
            'isp_ip',
        ]


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
            'wan_ip',
            'local_asn',
            'remote_asn',
        ]

    def clean_remote_asn(self, *args, **kwargs):
        remote_asn = self.cleaned_data['remote_asn']
        if(remote_asn < 65000):
            # TODO: finish the code!
            raise forms.ValidationError('lolmax1')
        return remote_asn
