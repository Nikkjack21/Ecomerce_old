from pyexpat import model
from django import forms
from . models import Account, UserProfile

class UserForm(forms.ModelForm):
    class Meta:
        model  = Account
        fields = ('first_name', 'last_name', 'email' ,'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            
            
            
            
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model   = UserProfile
        fields  = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture' )
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            
            
            
            
        }
