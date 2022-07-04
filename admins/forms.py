from cartapp.models import Coupon, ProductOffer, CategoryOffer
from django import forms
from dataclasses import fields
import datetime

from orders.models import Order
from django.core import validators

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

    def clean_discount(self):
        discount     = self.cleaned_data['discount']

        if discount > 80:
            raise forms.ValidationError('Offer cannot exceed 80%')
        return discount




class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = '__all__'
        widgets = {
            'valid_from': DateTimeLocal(),
            'valid_to': DateTimeLocal(),
        }
    def clean_discount(self):
        discount     = self.cleaned_data['discount']

        if discount > 80:
            raise forms.ValidationError('Offer cannot exceed 80%')
        return discount





class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields= '__all__'





class CouponAdminForm(forms.ModelForm):   
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'valid_from': DateTimeLocal(),
            'valid_to': DateTimeLocal(),
        }