from django.db import models
from django.utils.translation import gettext_lazy as _
from closet.models import Closet


class Router(models.Model):
    class WanTypeChoices(models.TextChoices):
        MPLS = 'MPLS', _('MPLS')
        P2P = 'Point-to-Point', _('Point-to-Point')

    class WanProviderChoices(models.TextChoices):
        ATT = 'AT&T', _('AT&T')
        BELLCANADA = 'Bell Canada', _('Bell Canada')
        CENTURYLINK = 'Century Link', _('Century Link')
        CHINATELCOM = 'China Telecom', _('China Telecom')
        DEUTSCHETELEKOM = 'Deutsche Telekom', _('Deutsche Telekom')
        EMBRATEL = 'Embratel', _('Embratel')
        FREE = 'Free', _('Free')
        GESTIONTELCOM = 'Gestion Telcom', _('Gestion Telcom')
        GLOBE = 'Globe', _('Globe')
        KDDI = 'KDDI', _('KDDI')
        KOREATELCOM = 'Korea Telcom', _('Korea Telcom')
        LEVEL3 = 'Level3', _('Level3')
        MCI = 'MCI', _('MCI')
        MXIS = 'MXIS', _('MXIS')
        NTTCOM = 'NTTCOM', _('NTTCOM')
        ORANGE = 'Orange', _('Orange')
        PCCW = 'PCCW', _('PCCW')
        PLDT = 'PLDT', _('PLDT')
        SINGTEL = 'Singtel', _('Singtel')
        SOFTBANK = 'Softbank', _('Softbank')
        TATA = 'Tata', _('Tata')
        TELCOMARGENTINA = 'Telcom Argentina', _('Telcom Argentina')
        TELCOMMALAYSIA = 'Telcom Malaysia', _('Telcom Malaysia')
        TELEFONICA = 'Telefonica', _('Telefonica')
        TELSTRA = 'Telstra', _('Telstra')
        TELUS = 'Telus', _('Telus')
        VERIZON = 'Verizon', _('Verizon')
        VODAFONE = 'Vodafone', _('Vodafone')
        ZAYO = 'Zayo', _('Zayo')

    hostname = models.CharField('Hostname', max_length=19)  # model_anchor
    loopback_ip = models.CharField(
        'Loopback IP', max_length=15, blank=True, null=True)  # brownfield_generated
    downlink_1_desc = models.CharField(
        'Downlink#1 Description', max_length=37, null=True)  # model_generated
    downlink_1_ip = models.CharField(
        'Downlink#1 IP', max_length=15, blank=True, null=True)  # brownfield_generated
    downlink_2_desc = models.CharField(
        'Downlink#2 Description', max_length=37, null=True)  # model_generated
    downlink_2_ip = models.CharField(
        'Downlink#2 IP', max_length=15, blank=True, null=True)  # brownfield_generated
    interlink_1_desc = models.CharField(
        'Interlink#1 Description', max_length=37, null=True)  # model_generated
    interlink_1_ip = models.CharField(
        'Interlink#1 IP', max_length=15, blank=True, null=True)  # brownfield_generated
    interlink_2_desc = models.CharField(
        'Interlink#2 Description', max_length=37, null=True)  # model_generated
    interlink_2_ip = models.CharField(
        'Interlink#2 IP', max_length=15, blank=True, null=True)  # brownfield_generated
    wan_type = models.CharField('WAN Type', choices=WanTypeChoices.choices,
                                default=WanTypeChoices.MPLS, max_length=14)  # greenfield_static
    wan_provider = models.CharField(
        'WAN Provider', choices=WanProviderChoices.choices, max_length=20)  # greenfield_static
    access_id = models.CharField(
        'Circuit Access ID', max_length=80)  # greenfield_static
    port_id = models.CharField(
        'Circuit Port ID', max_length=80)  # greenfield_static
    access_bw = models.IntegerField(
        'Circuit Access Bandwidth')  # greenfield_static
    port_bw = models.IntegerField(
        'Circuit Port Bandwidth')  # greenfield_static
    wan_link_cidr = models.CharField(
        'WAN Link CIDR', max_length=18)  # greenfield_static
    local_asn = models.IntegerField(
        'Local BGP ASN')  # greenfield_static
    remote_asn = models.IntegerField(
        'Remote BGP ASN')  # greenfield_static
    other_router_loopback_ip = models.CharField(
        'Other Router Loopback IP', max_length=15, blank=True, null=True)  # TODO: model_generated
    other_router_hostname = models.CharField(
        'Other Router Hostname', max_length=19, null=True)  # model_generated
    isp_ip = models.CharField(
        'ISP IP', max_length=15, blank=True, null=True)  # brownfield_generated
    closet = models.ForeignKey(
        Closet, on_delete=models.CASCADE)  # model_anchor

    '''
    ****programatically generated****
    dna_token
    loopback_desc
    netflow_collector
    qos_config
    downlink_1_intr = models.CharField(max_length=20)
    downlink_2_intr = models.CharField(max_length=20)
    lan_qos_policy
    interlink_1_intr = models.CharField(max_length=20)
    interlink_2_intr = models.CharField(max_length=20)
    wan_intr = models.CharField(max_length=20)
    wan_qos_policy
    community_string
    '''
