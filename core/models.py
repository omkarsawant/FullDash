from django.db import models
from django.utils.translation import gettext_lazy as _


class CoreGeneral(models.Model):
    hostname = models.CharField('Router Hostname', max_length=19)
    loopback_ip = models.GenericIPAddressField('Loopback IP', protocol='IPv4')
    loopback_desc = models.CharField(max_length=26)
    uplink_1_intr = models.CharField(max_length=20)
    uplink_1_desc = models.CharField(max_length=37)
    uplink_1_ip = models.GenericIPAddressField(
        'Uplink 1 IP', protocol='IPv4')
    uplink_2_intr = models.CharField(max_length=20)
    uplink_2_desc = models.CharField(max_length=37)
    uplink_2_ip = models.GenericIPAddressField(
        'Uplink 2 IP', protocol='IPv4')
    intralink_1_intr = models.CharField(max_length=20)
    intralink_2_intr = models.CharField(max_length=20)
    interlink_1_intr = models.CharField(max_length=20)
    interlink_2_intr = models.CharField(max_length=20)
    wlc_intr_1 = models.CharField(max_length=20)
    wlc_intr_2 = models.CharField(max_length=20)
    wlc_ha_intr = models.CharField(max_length=20)
    dual_intr_1 = models.CharField(max_length=20)
    dual_intr_2 = models.CharField(max_length=20)


class CoreVlan(models.Model):
    class VlanTypeChoices(models.TextChoices):
        DATA = 'data', _('Data')
        SECURITY = 'security', _('Security')
        VOICE = 'voice', _('Voice')
        VOICE_INFRA = 'voice_infra', _('Voice Infrastructure')
        SERVER = 'server', _('Server')

    vlan_type = models.CharField(
        'VLAN Type', choices=VlanTypeChoices.choices, max_length=20)
    vlan_id = models.IntegerField('VLAN ID')
    vlan_ip = models.GenericIPAddressField('SVI IP', protocol='IPv4')
    vlan_subnet = models.GenericIPAddressField('SVI Subnet', protocol='IPv4')
