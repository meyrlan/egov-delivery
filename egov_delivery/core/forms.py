from django import forms
from core.models import *


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('iin', 'cashback', 'phone_number')


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['region', 'city',
                  'street', 'house_number', 'apartment',
                  'entrance', 'floor', 'block', 'house_name', 'additional_information']
