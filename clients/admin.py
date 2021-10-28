from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from clients.models import Client, Domain

admin.site.register(Domain)


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name')
