from cartapp.models import ProductOffer
from django import forms
from dataclasses import fields
import datetime


class DateTimeLocal(forms.DateTimeInput):
    input_type = 'datetime-local'
    color ='Red'

class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = '__all__'
        widgets = {
            'valid_from': DateTimeLocal(),
            'valid_to': DateTimeLocal(),
        }