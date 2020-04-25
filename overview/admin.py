from django.contrib import admin
from .models import ExcludedSubnet, Supernet

admin.site.register(ExcludedSubnet)
admin.site.register(Supernet)
