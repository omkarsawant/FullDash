from django.db import models
from closets.models import Closets


class Router(models.Model):
    hostname = models.CharField('Router Hostname', max_length=19)
    loopback_ip = models.GenericIPAddressField('Loopback IP', protocol='IPv4')
    downlink_1_intr = models.CharField(max_length=20)
    downlink_1_desc = models.CharField(max_length=37)
    downlink_1_ip = models.GenericIPAddressField(
        'Downlink 1 IP', protocol='IPv4')
    downlink_2_intr = models.CharField(max_length=20)
    downlink_2_desc = models.CharField(max_length=37)
    downlink_2_ip = models.GenericIPAddressField(
        'Downlink 1 IP', protocol='IPv4')
    interlink_1_intr = models.CharField(max_length=20)
    interlink_1_desc = models.CharField(max_length=37)
    interlink_1_ip = models.GenericIPAddressField(
        'Interlink 1 IP', protocol='IPv4')
    interlink_2_intr = models.CharField(max_length=20)
    interlink_2_desc = models.CharField(max_length=37)
    interlink_2_ip = models.GenericIPAddressField(
        'Interlink 1 IP', protocol='IPv4')
    wan_intr = models.CharField(max_length=20)
    wan_desc = models.CharField(max_length=200)
    wan_ip = models.GenericIPAddressField(
        'WAN IP', protocol='IPv4')
    wan_bw = models.IntegerField('Circuit Bandwidth')
    local_asn = models.IntegerField('Local BGP ASN')
    remote_asn = models.IntegerField('Remote BGP ASN')
    closet = models.ForeignKey(Closets, on_delete=models.CASCADE)
