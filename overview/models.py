from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Overview(models.Model):

    class ProjectTypeChoices(models.TextChoices):
        BROWNFIELD = 'brownfield', _('Brownfield')
        GREENFIELD = 'greenfield', _('Greenfield')

    class NearestDcChoice(models.TextChoices):
        AM1 = 'am1', _('AM1')
        AM2 = 'am2', _('AM2')

    address = models.CharField(
        'Site Address', blank=True, max_length=512, null=True)
    capacity = models.PositiveIntegerField(
        'Site Capacity', blank=True, null=True)
    crest = models.IntegerField('Site CREST ID')
    headcount = models.PositiveIntegerField(
        'Site Headcount', blank=True, null=True)
    nearest_dc = models.CharField('Nearest DC to Site',
                                  blank=True, choices=NearestDcChoice.choices, max_length=4, null=True)
    project_type = models.CharField('Type of Project',
                                    choices=ProjectTypeChoices.choices, default=ProjectTypeChoices.GREENFIELD, max_length=10,)

    def get_absolute_url(self):
        return reverse('overview-update', kwargs={'id': self.id})
