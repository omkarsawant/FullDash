from django.db import models
from django.utils.translation import gettext_lazy as _
from closet.models import Closet


class Router(models.Model):
    class WanTypeChoices(models.TextChoices):
        MPLS = 'mpls', _('MPLS')
        P2P = 'p2p', _('Point-to-Point')

    class WanProviderChoices(models.TextChoices):
        ATT = 'att', _('AT&T')
        BELLCANADA = 'bellcanada', _('Bell Canada')
        CENTURYLINK = 'centurylink', _('Century Link')
        CHINATELCOM = 'chinatelcom', _('China Telecom')
        DEUTSCHETELEKOM = 'deutschetelekom', _('Deutsche Telekom')
        EMBRATEL = 'embratel', _('Embratel')
        FREE = 'free', _('Free')
        GESTIONTELCOM = 'gestiontelcom', _('Gestion Telcom')
        GLOBE = 'globe', _('Globe')
        KDDI = 'kddi', _('KDDI')
        KOREATELCOM = 'koreatelcom', _('Korea Telcom')
        LEVEL3 = 'level3', _('Level3')
        MCI = 'mci', _('MCI')
        MXIS = 'mxis', _('MXIS')
        NTTCOM = 'nttcom', _('NTTCOM')
        ORANGE = 'orange', _('Orange')
        PCCW = 'pccw', _('PCCW')
        PLDT = 'pldt', _('PLDT')
        SINGTEL = 'singtel', _('Singtel')
        SOFTBANK = 'softbank', _('Softbank')
        TATA = 'tata', _('Tata')
        TELCOMARGENTINA = 'telcomargentina', _('Telcom Argentina')
        TELCOMMALAYSIA = 'telcommalaysia', _('Telcom Malaysia')
        TELEFONICA = 'telefonica', _('Telefonica')
        TELSTRA = 'telstra', _('Telstra')
        TELUS = 'telus', _('Telus')
        VERIZON = 'verizon', _('Verizon')
        VODAPHONE = 'vodaphone', _('Vodafone')
        ZAYO = 'zayo', _('Zayo')

    hostname = models.CharField('Hostname', max_length=19)  # model
    loopback_cidr = models.CharField(
        'Loopback CIDR', max_length=18, blank=True, null=True)  # brownfield
    downlink_1_desc = models.CharField(
        'Downlink#1 Description', max_length=37, null=True)  # model
    downlink_1_cidr = models.CharField(
        'Downlink#1 CIDR', max_length=18, blank=True, null=True)  # brownfield
    downlink_2_desc = models.CharField(
        'Downlink#2 Description', max_length=37, null=True)  # model
    downlink_2_cidr = models.CharField(
        'Downlink#2 CIDR', max_length=18, blank=True, null=True)  # brownfield
    interlink_1_desc = models.CharField(
        'Interlink#1 Description', max_length=37, null=True)  # model
    interlink_1_cidr = models.CharField(
        'Interlink#1 CIDR', max_length=18, blank=True, null=True)  # brownfield
    interlink_2_desc = models.CharField(
        'Interlink#2 Description', max_length=37, null=True)  # model
    interlink_2_cidr = models.CharField(
        'Interlink#2 CIDR', max_length=18, blank=True, null=True)  # brownfield
    wan_type = models.CharField('WAN Type', choices=WanTypeChoices.choices,
                                default=WanTypeChoices.MPLS, max_length=10, null=True)  # greenfield
    wan_provider = models.CharField(
        'WAN Provider', choices=WanProviderChoices.choices, max_length=20, null=True)  # greenfield
    access_id = models.CharField(
        'Circuit Access ID', max_length=80, null=True)  # greenfield
    port_id = models.CharField(
        'Circuit Port ID', max_length=80, null=True)  # greenfield
    access_bw = models.IntegerField(
        'Circuit Access Bandwidth', null=True)  # greenfield
    port_bw = models.IntegerField(
        'Circuit Port Bandwidth', null=True)  # greenfield
    wan_cidr = models.CharField(
        'WAN CIDR', max_length=18, null=True)  # greenfield
    local_asn = models.IntegerField('Local BGP ASN', null=True)  # greenfield
    remote_asn = models.IntegerField('Remote BGP ASN', null=True)  # greenfield
    other_router_loopback_cidr = models.CharField(
        'Other Router Loopback CIDR', max_length=18, blank=True, null=True)  # brownfield
    other_router_hostname = models.CharField(
        'Other Router Hostname', max_length=19, null=True)  # model
    isp_cidr = models.CharField(
        'ISP CIDR', max_length=18, blank=True, null=True)  # brownfield
    closet = models.ForeignKey(Closet, on_delete=models.CASCADE)  # model

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
