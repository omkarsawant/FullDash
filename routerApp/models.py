from django.db import models


class Router4331(models.Model):
    hostname = models.CharField(max_length=10)
    loopback = models.GenericIPAddressField(protocol='IPv4')


class Router4351(models.Model):
    hostname = models.CharField(max_length=10)
    loopback = models.GenericIPAddressField(protocol='IPv4')
