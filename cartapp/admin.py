from django.contrib import admin
from .models import Cart, CartItem, Coupon, CouponUsedUser, ProductOffer, CategoryOffer
# Register your models here.


class ProductOfferAdmin(admin.ModelAdmin):
    list_diplay=['product','active']
    list_filter = ['product']



class CouponAdmin(admin.ModelAdmin):
    list_display =['code','valid_from','valid_to','discount']
    list_filter = ['active']
    search_fields = ['code']




admin.site.register(ProductOffer,ProductOfferAdmin)
admin.site.register(CategoryOffer)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CouponUsedUser)

