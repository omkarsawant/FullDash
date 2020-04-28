from django.db import models
from django.utils.translation import gettext_lazy as _

from closet.models import Closet


class AccessSwitch(models.Model):

    class AccessChoices(models.TextChoices):
        CATALYST_3850 = 'catalyst_3850', _('Catalyst 3850')
        CATALYST_9300 = 'catalyst_9300', _('Catalyst 9300')

    class SwitchCountChoices(models.IntegerChoices):
        SC_1 = 1, _('1')
        SC_2 = 2, _('2')
        SC_3 = 3, _('3')
        SC_4 = 4, _('4')
        SC_5 = 5, _('5')
        SC_6 = 6, _('6')
        SC_7 = 7, _('7')
        SC_8 = 8, _('8')

    hostname = models.CharField('Hostname', max_length=19)  # model
    stack_model = models.CharField(
        'Access Stack Model', choices=AccessChoices.choices, default=AccessChoices.CATALYST_9300, max_length=13, null=True)  # greenfield
    switch_count = models.IntegerField(
        'Total Switch#', choices=SwitchCountChoices.choices, null=True)  # greenfield
    mgig_count = models.IntegerField(
        'MGig Switch#', choices=SwitchCountChoices.choices, null=True)  # greenfield
    loopback_ip = models.CharField(
        'Loopback IP', max_length=15, blank=True, null=True)  # brownfield
    uplink_1_desc = models.CharField(
        'Uplink#1 Description', max_length=37, null=True)  # model
    uplink_1_ip = models.CharField(
        'Uplink#1 IP', max_length=15, blank=True, null=True)  # brownfield
    uplink_2_desc = models.CharField(
        'Uplink#2 Description', max_length=37, null=True)  # model
    uplink_2_ip = models.CharField(
        'Uplink#2 IP', max_length=15, blank=True, null=True)  # brownfield
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
    end_intr = models.CharField('End Interface', max_length=21)  # greenfield
    access_vlan = models.IntegerField('Access VLAN')  # greenfield
    voice_vlan = models.IntegerField('Voice VLAN')  # greenfield
    legacy_qos = models.BooleanField(
        'Apply Legacy QoS', default=False)  # greenfield
    access_switch = models.ForeignKey(
        AccessSwitch, on_delete=models.CASCADE)  # model


class Vlan(models.Model):
    class MaskLengthChoices(models.TextChoices):
        ML_23 = 'ml_23', _('/23')
        ML_24 = 'ml_24', _('/24')
        ML_25 = 'ml_25', _('/25')
        ML_26 = 'ml_26', _('/26')
        ML_27 = 'ml_27', _('/27')
        ML_28 = 'ml_28', _('/28')
        ML_29 = 'ml_29', _('/29')

    class VlanTypeChoices(models.TextChoices):
        DATA = 'data', _('Data')
        VOICE = 'voice', _('Voice')
        SECURITY = 'security', _('Security')
        SERVER = 'server', _('Server')
        VOICE_SERVER = 'voice_server', _('Voice Server')

    vlan_type = models.CharField(
        'VLAN Type', choices=VlanTypeChoices.choices, max_length=12)  # greenfield
    vlan_id = models.IntegerField('VLAN ID')  # brownfield
    name = models.CharField('VLAN Name', max_length=32)  # brownfield
    svi_ip = models.CharField(
        'SVI IP', max_length=15, blank=True, null=True)  # brownfield
    svi_mask_length = models.CharField(
        'SVI Mask', choices=MaskLengthChoices.choices, max_length=5)  # greenfield
    access_switch = models.ForeignKey(
        AccessSwitch, on_delete=models.CASCADE)  # model

    '''
    ****programatically generated****
    vlan_desc
    helper_address --> mutiple per model record
    nac_address --> mutiple per model record
    
    '''
