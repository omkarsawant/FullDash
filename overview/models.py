from django.db import models
from onboard.models import Site


class Supernet(models.Model):
    supernet = models.CharField(
        'Supernet CIDR', max_length=18)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)


class ExcludedSubnet(models.Model):
    subnet = models.CharField(
        'Excluded Subnet CIDR', max_length=18)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
