from django.db import models
from django.utils.translation import gettext_lazy as _


class Site(models.Model):
    class CoreChoices(models.TextChoices):
        NO_CORE = 'No Core Layer', _('No Core Layer')
        CATALYST_3850 = 'Catalyst 3850', _('Catalyst 3850')
        CATALYST_6840 = 'Catalyst 6840', _('Catalyst 6840')
        CATALYST_6880 = 'Catalyst 6880', _('Catalyst 6880')
        CATALYST_9500 = 'Catalyst 9500', _('Catalyst 9500')

    class NearestDcChoices(models.TextChoices):
        AM1 = 'AM1', _('AM1')
        AM2 = 'AM2', _('AM2')

    class NetworkTypeChoices(models.TextChoices):
        MICRO_BRANCH = 'Micro Branch', _('Micro Branch')
        MINI_BRANCH = 'Mini Branch', _('Mini Branch')
        SMALL_BRANCH = 'Small Branch', _('Small Branch')
        MEDIUM_BRANCH_1 = 'Medium Branch (1-2 Floors)', _(
            'Medium Branch (1-2 Floors)')
        MEDIUM_BRANCH_2 = 'Medium Branch (3-10 Floors)', _(
            'Medium Branch (3-10 Floors)')
        LARGE_BRANCH = 'Large Branch', _('Large Branch')
        MEDIUM_CAMPUS = 'Medium Campus', _('Medium Campus')
        LARGE_CAMPUS = 'Large Campus', _('Large Campus')

    class ProjectTypeChoices(models.TextChoices):
        BROWNFIELD = 'Brownfield', _('Brownfield')
        GREENFIELD = 'Greenfield', _('Greenfield')

    class RouterChoices(models.TextChoices):
        ASR_1001_X = 'ASR 1001-X', _('ASR 1001-X')
        ASR_1001_HX = 'ASR 1001-HX', _('ASR 1001-HX')
        ISR_4331 = 'ISR 4331', _('ISR 4331')
        ISR_4351 = 'ISR 4351', _('ISR 4351')
        ISR_4451 = 'ISR 4451', _('ISR 4451')

    class ServerChoices(models.TextChoices):
        NO_SERVER = 'No Server Layer', _('No Server Layer')
        CATALYST_4500 = 'Catalyst 4500', _('Catalyst 4500')
        CATALYST_9500 = 'Catalyst 9500', _('Catalyst 9500')

    crest = models.IntegerField('CREST ID')  # greenfield_static
    project_type = models.CharField('Projet Type',
                                    choices=ProjectTypeChoices.choices, default=ProjectTypeChoices.GREENFIELD, max_length=10)  # greenfield_static
    network_name = models.CharField(
        'Network Name', max_length=96)  # model_anchor
    address = models.CharField(
        'Site Address', max_length=96)  # model_anchor
    capacity = models.IntegerField(
        'Site Capacity')  # model_anchor
    headcount = models.IntegerField(
        'Site Headcount')  # model_anchor
    network_type = models.CharField(
        'Network Type', choices=NetworkTypeChoices.choices, default=NetworkTypeChoices.MICRO_BRANCH, max_length=27)  # model_anchor
    nearest_dc = models.CharField('Nearest DC',
                                  choices=NearestDcChoices.choices, max_length=4)  # model_anchor
    router = models.CharField(
        'Router Layer', choices=RouterChoices.choices, max_length=11)  # brownfield_anchor
    core = models.CharField(
        'Core Layer', choices=CoreChoices.choices, max_length=13)  # brownfield_anchor
    server = models.CharField(
        'Server Layer', choices=ServerChoices.choices, max_length=15)  # brownfield_anchor
    # model signals
    signal_created_access = models.BooleanField(
        'Access Created', null=True)  # signal
    signal_duplicate_vlan = models.BooleanField(
        'Duplicate VLAN', null=True)  # signal
    signal_exception_site = models.BooleanField(
        'Site Non-standard', null=True)  # signal
    signal_onboarded_site = models.BooleanField(
        'Site Onboarded', null=True)  # signal
    signal_present_core = models.BooleanField(
        'Core Present', null=True)  # signal
    signal_present_server = models.BooleanField(
        'Server Present', null=True)  # signal
    signal_updated_access = models.BooleanField(
        'Access Updated', null=True)  # signal
    signal_updated_core = models.BooleanField(
        'Core Updated', null=True)  # signal
    signal_updated_server = models.BooleanField(
        'Server Updated', null=True)  # signal
    signal_updated_wan = models.BooleanField(
        'WAN Updated', null=True)  # signal
