from django.contrib import admin
from .models import Cart, CartItem, ProductOffer, CategoryOffer
# Register your models here.


class ProductOfferAdmin(admin.ModelAdmin):
    list_diplay=['product','active']
    list_filter = ['product']


admin.site.register(ProductOffer,ProductOfferAdmin)
admin.site.register(CategoryOffer)
admin.site.register(Cart)
admin.site.register(CartItem)

