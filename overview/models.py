from django.db import models
from django.urls import reverse


class Overview(models.Model):
    crest = models.IntegerField()

    def get_overview_create_url(self):
        return reverse('overview:create')
