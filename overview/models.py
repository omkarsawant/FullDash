from django.db import models
from onboard.models import Site


class Supernet(models.Model):
    supernet_cidr = models.CharField(
        'Supernet CIDR', max_length=18)  # greenfield_static
    site = models.ForeignKey(Site, on_delete=models.CASCADE)  # model_anchor


class ExcludedSubnet(models.Model):
    subnet_cidr = models.CharField(
        'Excluded Subnet CIDR', max_length=18)  # greenfield_static
    site = models.ForeignKey(Site, on_delete=models.CASCADE)  # model_anchor
