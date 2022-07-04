from django.urls import path

import cartapp.views
from .import views 



urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('otp', views.otp, name='otp'),
    path('code/', views.otpcode, name='code'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('my_account/',views.my_account, name='my_account'),
    path('my_wallet/', views.my_wallet, name='my_wallet'),
    path('all_products/', views.p_view, name='all_products'),

    path('main_p_store/<int:id>/', views.main_p_view, name='p_store'),
    path('products/<int:id>/', views.pro_store, name='products_by_cat'),
    
    path('editpro/<int:id>/', views.editProfile, name='edit_profile'),
    path('change_password/', views.changePassword, name='change_password'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_user_actions/<int:id>/', views.order_user_actions, name='order_user_actions'),
    path('order_return/<int:id>/', views.order_return, name='order_return'),
    
    path('user_address/', views.user_address, name='user_address'),
    path('add_address/', views.add_address, name='add_addresss'),
    path('checkout_add_address/', views.checkout_add_address, name="checkout_add_address"),
    path('buy_add_address/', cartapp.views.buy_add_address , name="buy_add_address"),
    path('edit_address/<int:id>/', views.edit_address, name="edit_address"),

    path('phone_number_verify/', views.phone_verfiy, name="phone_number_verify"),
    path('phone_number_verification//', views.phone_verification, name="phone_number_verification"),
    path('otp_verification/<int:phone_number>/', views.otp_verification, name="otp_verification"),
    path('referel_add/', views.add_ref, name='referel_add'),
    path('cod_ref/', views.ref_cod_v, name="ref_code"),
    # path('<slug:category_slug>/', views.p_view, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.p_details, name='products_by_category'),

    
]