from cartapp.models import ProductOffer, CategoryOffer
from django import forms
from dataclasses import fields
import datetime

from orders.models import Order


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
class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = '__all__'
        widgets = {
            'valid_from': DateTimeLocal(),
            'valid_to': DateTimeLocal(),
        }





class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields= '__all__'