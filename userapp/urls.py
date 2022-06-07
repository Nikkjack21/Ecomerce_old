from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('otp', views.otp, name='otp'),
    path('code/', views.otpcode, name='code'),
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('details/', views.p_details, name='details'),
    path('products/', views.p_view, name='products'),
    path('<slug:category_slug>/', views.p_view, name='products_by_category'),
    

   
   
    
]