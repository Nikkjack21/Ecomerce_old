from django.contrib import admin
from .models import Account, UserProfile, Wallet, Address
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'last_login','date_joined', 'is_active' )

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'country')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address_line', 'pincode', 'city','state' )





admin.site.register(Wallet)
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)