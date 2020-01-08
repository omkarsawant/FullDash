from django.db import models


class Router(models.Model):
    INTERFACE_CHOICES = [
        ('GigabitEthernet0/0/0', 'GigE0/0/0'),
        ('GigabitEthernet0/0/1', 'GigE0/0/1'),
    ]
    hostname = models.CharField(max_length=19)
    loopback = models.GenericIPAddressField(protocol='IPv4')
    interface = models.CharField(
        max_length=100, choices=INTERFACE_CHOICES, default='GigabitEthernet0/0/0')
