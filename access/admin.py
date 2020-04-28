from django.contrib import admin
from .models import AccessSwitch, AccessPortBlock, Vlan

admin.site.register(AccessSwitch)
admin.site.register(AccessPortBlock)
admin.site.register(Vlan)
