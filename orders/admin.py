from django.contrib import admin
from requests import request
from .models import Payment, Order, OrderProduct, RazorPay

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'phone', 'email', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'phone']
    list_per_page  = 10




admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(RazorPay)
