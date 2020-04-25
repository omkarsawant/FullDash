from django.db import models
from django.utils.translation import gettext_lazy as _
from onboard.models import Site


class Closet(models.Model):
    class CategoryChoices(models.TextChoices):
        IDF = 'idf', _('IDF')
        MDF = 'mdf', _('MDF')
        MDF_IDF = 'mdf_idf', _('MDF & IDF')

    floor = models.IntegerField('Floor')
    category = models.CharField('Closet Type', max_length=9,
                                choices=CategoryChoices.choices, default=CategoryChoices.IDF)
    closet = models.CharField('Closet', max_length=4, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
