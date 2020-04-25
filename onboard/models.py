from django.db import models
from django.utils.translation import gettext_lazy as _


class Site(models.Model):
    class CoreChoices(models.TextChoices):
        NO_CORE = 'no_core', _('No Core Layer')
        CATALYST_3850 = 'catalyst_3850', _('Catalyst 3850')
        CATALYST_6840 = 'catalyst_6840', _('Catalyst 6840')
        CATALYST_6880 = 'catalyst_6880', _('Catalyst 6880')
        CATALYST_9500 = 'catalyst_9500', _('Catalyst 9500')

    class NearestDcChoices(models.TextChoices):
        AM1 = 'am1', _('AM1')
        AM2 = 'am2', _('AM2')

    class NetworkTypeChoices(models.TextChoices):
        MICRO_BRANCH = 'micro_branch', _('Micro Branch')
        MINI_BRANCH = 'mini_branch', _('Mini Branch')
        SMALL_BRANCH = 'small_branch', _('Small Branch')
        MEDIUM_BRANCH_1 = 'medium_branch_1', _('Medium Branch (1-2 Floors)')
        MEDIUM_BRANCH_2 = 'medium_branch_2', _('Medium Branch (3-10 Floors)')
        LARGE_BRANCH = 'large_branch', _('Large Branch')
        MEDIUM_CAMPUS = 'medium_campus', _('Medium Campus')
        LARGE_CAMPUS = 'large_campus', _('Large Campus')

    class ProjectTypeChoices(models.TextChoices):
        BROWNFIELD = 'brownfield', _('Brownfield')
        GREENFIELD = 'greenfield', _('Greenfield')

    class RouterChoices(models.TextChoices):
        ASR_1001_X = 'asr_1001_x', _('ASR 1001-X')
        ASR_1001_HX = 'asr_1001_hx', _('ASR 1001-HX')
        ISR_4331 = 'isr_4331', _('ISR 4331')
        ISR_4351 = 'isr_4351', _('ISR 4351')
        ISR_4451 = 'isr_4451', _('ISR 4451')

    class ServerChoices(models.TextChoices):
        NO_SERVER = 'no_server', _('No Server Layer')
        CATALYST_4500 = 'catalyst_4500', _('Catalyst 4500')
        CATALYST_9500 = 'catalyst_9500', _('Catalyst 9500')

    crest = models.IntegerField('CREST ID')
    project_type = models.CharField('Projet Type',
                                    choices=ProjectTypeChoices.choices, default=ProjectTypeChoices.GREENFIELD, max_length=10)
    network_name = models.CharField('Network Name', max_length=96)
    address = models.CharField(
        'Site Address', max_length=96)
    capacity = models.IntegerField(
        'Site Capacity')
    headcount = models.IntegerField(
        'Site Headcount')
    network_type = models.CharField(
        'Network Type', choices=NetworkTypeChoices.choices, default=NetworkTypeChoices.MICRO_BRANCH, max_length=27)
    nearest_dc = models.CharField('Nearest DC',
                                  choices=NearestDcChoices.choices, max_length=4)
    router = models.CharField(
        'Router Layer', choices=RouterChoices.choices, max_length=11)
    core = models.CharField(
        'Core Layer', choices=CoreChoices.choices, max_length=13)
    server = models.CharField(
        'Server Layer', choices=ServerChoices.choices, max_length=15)
    # signals
    signal_exception_site = models.BooleanField(
        'Site Non-standard', null=True)
    signal_onboarded_site = models.BooleanField(
        'Site Onboarded', null=True)
    signal_present_core = models.BooleanField(
        'Core Present', null=True)
    signal_present_server = models.BooleanField(
        'Server Present', null=True)
    signal_updated_access = models.BooleanField(
        'Access Updated', null=True)
    signal_updated_core = models.BooleanField(
        'Core Updated', null=True)
    signal_updated_server = models.BooleanField(
        'Server Updated', null=True)
    signal_updated_wan = models.BooleanField(
        'WAN Updated', null=True)
