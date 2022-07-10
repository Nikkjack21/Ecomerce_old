from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    
    path('adminsignin/', views.admin_signin, name='admin_signin'),
    path('adminhome', views.admin_home, name='admin_home'),
    path('out/', views.admin_out),
    path('user_details', views.users_details, name='details'),
    path('userAction/<int:id>', views.action_user, name='action_user'),
    path('category', views.cate_view, name='category' ),
    path('main_cat/', views.main_view, name='main_cat'),
    path('main_add/', views.main_add, name="main_add"),
    path('main_del/<int:id>/', views.main_del, name="main_del"),
    path('add_cate', views.cate_add, name='AddCategory'), 
    path('delete/<int:id>', views.cate_del, name='delete_cat'),
    path('edit/<int:id>', views.cate_edit, name='EditCategory' ),
    path('product_view', views.product_view, name='product_view'),
    path('add_pro', views.prouct_add, name='AddPro'),
    path('del_pro/<int:id>', views.product_delete, name='deletePro'),
    path('edit_pro/<int:id>', views.product_edit, name='editProduct'),
    path('order_list', views.order_list, name='order_list'),
    path('order_actions/<int:id>/', views.order_actions, name='order_actions'),
    path('order_status/<int:id>/', views.change_status, name='change_status'),
    path('product_offer/', views.offer_product, name='product_offer'),
    path('add_pro_offer/', views.add_offer_pro, name='add_pro_offer'),
    path('edit_pro_offer/<int:id>/', views.edit_pro_offer, name='edit_pro_offer'),
    path('delete_pro_offer/<int:id>/', views.delete_pro_offer, name='delete_pro_offer'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('monthly_report/<int:date>/', views.monthly_report, name='monthly_report'),
    path('year_report/<int:date>/', views.yearly_report, name='year_report'),
    path('show_result/',views.show_result, name='show_result'),
    path('cat_offer/', views.offer_category, name='cat_offer'),
    path('add_cat_offer/', views.add_offer_cat, name='add_cat_offer'),
    path('edit_cat_offer/<int:id>/', views.edit_cat_offer, name='edit_cat_offer'),
    path('delete_cat_offer/<int:id>/', views.delete_cat_offer, name='delete_cat_offer'),
    path('coupon_list/', views.coupon_list, name='coupon_list'),
    path('coupon_add/', views.add_coupon, name='coupon_add'),
    path('coupon_edit/<int:id>/', views.edit_coupon, name="coupon_edit"),
    path('coupon_delete/<int:id>/', views.delete_coupon, name="coupon_delete"),

   
]

