from django.db import models


class Router(models.Model):
    hostname = models.CharField(max_length=10)
    loopback = models.GenericIPAddressField(protocol='IPv4')
