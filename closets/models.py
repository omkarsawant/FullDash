from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from overview.models import Overview


class Closets(models.Model):
    class CategoryChoices(models.TextChoices):
        IDF = 'idf', _('IDF')
        MDF = 'mdf', _('MDF')
        MDF_IDF = 'mdf_idf', _('MDF & IDF')

    floor = models.IntegerField('Floor Number')
    category = models.CharField('Type of Closet', max_length=9,
                                choices=CategoryChoices.choices, default=CategoryChoices.IDF)
    overview = models.ForeignKey(Overview, on_delete=models.CASCADE)
