from django.db import models
from django.utils.translation import gettext_lazy as _
from closet.models import Closet


class AccessSwitch(models.Model):
    hostname = models.CharField('Hostname', max_length=19)  # model
    loopback_ip = models.CharField(
        'Loopback IP', max_length=18, blank=True, null=True)  # brownfield
    uplink_1_desc = models.CharField(
        'Uplink#1 Description', max_length=37, null=True)  # model
    uplink_1_ip = models.CharField(
        'Uplink#1 IP', max_length=18, blank=True, null=True)  # brownfield
    uplink_2_desc = models.CharField(
        'Uplink#2 Description', max_length=37, null=True)  # model
    uplink_2_ip = models.CharField(
        'Uplink#2 IP', max_length=18, blank=True, null=True)  # brownfield
    closet = models.ForeignKey(Closet, on_delete=models.CASCADE)  # model


'''
    ****programatically generated****
    number --> multiple per model record
    priority --> multiple per model record
    dna_token
    qos_config
    loopback_desc
    uplink_1_intr
    uplink_2_intr
'''


class AccessPortBlock(models.Model):
    start_intr = models.CharField(
        'Start Interface', max_length=21)  # greenfield
    end_intr = models.CharField('Start Interface', max_length=21)  # greenfield
    access_vlan = models.IntegerField('Access VLAN')  # greenfield
    voice_vlan = models.IntegerField('Voice VLAN')  # greenfield
    legacy_qos = models.BooleanField(
        'Legacy QoS Required', null=True)  # greenfield
    access_switch = models.ForeignKey(
        AccessSwitch, on_delete=models.CASCADE)  # model


class Vlan(models.Model):
    class VlanTypeChoices(models.TextChoices):
        DATA = 'data', _('Data')
        VOICE = 'voice', _('Voice')
        SECURITY = 'security', _('Security')
        SERVER = 'server', _('Server')
        VOICE_SERVER = 'voice_server', _('Voice Server')

    vlan_type = models.Charfield(
        'VLAN Type', choices=VlanTypeChoices.choices, default=VlanTypeChoices.DATA, max_length=12)  # greenfield
    vlan_id = models.IntegerField('VLAN ID')  # brownfield
    name = models.CharField('VLAN Name', max_length=32)  # brownfield
    svi_cidr = models.CharField(
        'SVI CIDR', max_length=18, blank=True, null=True)  # brownfield
    access_switch = models.ForeignKey(
        AccessSwitch, on_delete=models.CASCADE)  # model

    '''
    ****programatically generated****
    vlan_desc
    helper_address --> mutiple per model record
    nac_address --> mutiple per model record
    
    '''
