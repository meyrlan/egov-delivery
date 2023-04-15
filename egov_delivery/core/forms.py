from django import forms
from core.models import *


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('iin',)
