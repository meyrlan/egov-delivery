from django.contrib import admin
from core.models import *
from core.forms import *


@admin.register(Client)
class ClientModelAdmin(admin.ModelAdmin):
    form = ClientForm
    list_display = (
        'firstname',
        'middlename',
        'lastname',
        'iin',
        'home_address',
        'cashback',
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields += ['firstname', 'middlename',
                                'lastname', 'home_address', 'cashback']
        return readonly_fields


@admin.register(ServiceCenter)
class ServiceCenterAdminModel(admin.ModelAdmin):
    list_display = (
        'name',
        'address',
    )


class UserAdminInline(admin.TabularInline):
    model = User


@admin.register(CourierCompany)
class CourierCompanyAdminModel(admin.ModelAdmin):
    list_display = (
        'name',
    )
    inlines = [
        UserAdminInline,
    ]


@admin.register(User)
class CourierAdminModel(admin.ModelAdmin):
    list_display = (
        "iin",
        "phone_number",
        "role",
        "courier_company",
        "service_center",
    )
    fields = (
        "iin",
        "password",
        "phone_number",
        "role",
        "courier_company",
        "service_center",
    )


@admin.register(Address)
class AddressAdminModel(admin.ModelAdmin):
    list_display = (
        "street",
        "house_number",
        "region",
        "city",
    )
    form = AddressForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields += ['lat', 'lng']
        return readonly_fields


@admin.register(DocumentOrder)
class DocumentOrderAdminModel(admin.ModelAdmin):
    list_display = (
        "request_id",
    )
