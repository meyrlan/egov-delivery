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
