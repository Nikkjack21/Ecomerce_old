from django.urls import path
from .import views


urlpatterns =[
    path('', views.cart, name="cart"),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy_now_checkout/<int:id>/', views.buy_now, name='buy_now_checkout'),
    path('coupon_apply/',views.coupon_apply,name='coupon_apply'),
    path('add_cart_ajax/', views.add_cart_ajax, name="add_cart_ajax"),

    
]