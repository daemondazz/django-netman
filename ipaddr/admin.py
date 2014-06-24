from django.contrib import admin

from models import Subnet, Address


class AddressInline(admin.TabularInline):
    fields = ['addr', 'hostname', 'description']
    model = Address


class SubnetAdmin(admin.ModelAdmin):
    list_display = ['network_addr', 'description']
    inlines = [AddressInline]


admin.site.register(Subnet, SubnetAdmin)
