from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('otp', views.otp, name='otp'),
    path('code/', views.otpcode, name='code'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('my_account/',views.my_account, name='my_account'),
    path('products/', views.p_view, name='products'),
    path('editpro/', views.editProfile, name='edit_profile'),
    path('change_password/', views.changePassword, name='change_password'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('<slug:category_slug>/', views.p_view, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.p_details, name='products_by_category'),
   
    
]