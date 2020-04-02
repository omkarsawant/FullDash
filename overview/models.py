from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Overview(models.Model):
    class CoreChoices(models.TextChoices):
        NO_CORE = 'no_core', _('No Core Layer')
        CATALYST_3850 = 'catalyst_3850', _('Catalyst 3850')
        CATALYST_6840 = 'catalyst_6840', _('Catalyst 6840')
        CATALYST_6880 = 'catalyst_6880', _('Catalyst 6880')
        CATALYST_9500 = 'catalyst_9500', _('Catalyst 9500')

    class NearestDcChoices(models.TextChoices):
        AM1 = 'am1', _('AM1')
        AM2 = 'am2', _('AM2')

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

    crest = models.IntegerField('Site CREST ID')
    project_type = models.CharField('Type of Project',
                                    choices=ProjectTypeChoices.choices, default=ProjectTypeChoices.GREENFIELD, max_length=10, null=True)
    address = models.CharField(
        'Site Address', blank=True, max_length=128, null=True)
    capacity = models.IntegerField(
        'Site Capacity', blank=True, null=True)
    headcount = models.IntegerField(
        'Site Headcount', blank=True, null=True)
    nearest_dc = models.CharField('Nearest DC to Site',
                                  blank=True, choices=NearestDcChoices.choices, max_length=4, null=True)
    router = models.CharField(
        'Router Layer', choices=RouterChoices.choices, max_length=11, null=True)
    core = models.CharField(
        'Core Layer', choices=CoreChoices.choices, max_length=13, null=True)
    server = models.CharField(
        'Server Layer', choices=ServerChoices.choices, max_length=15, null=True)


class StaticSummary(models.Model):
    network = models.GenericIPAddressField(
        'Summary Subnet Network', protocol='IPv4')
    mask = models.GenericIPAddressField('Summary Subnet Mask', protocol='IPv4')
    overview = models.ForeignKey(Overview, on_delete=models.CASCADE)
