from django.urls import path
from .import views
urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('payments/', views.payment, name='payments'),
    path('cod/<str:order_number>/',views.cash_on_delivery,name='cash_on_delivery'),
    path('success/', views.order_complete, name='success'),
    path('razor_success/', views.razor_success, name='razor_success'),
    path('buy_razor_success/', views.buy_razor_success, name="razor_success_pay"),
    path('buy_now_place_order/<int:id>', views.buy_now_place_order, name="buy_now_place_order"),
    path('buy_now_payments/<int:id>/', views.buy_paypal, name='buy_now_pay'),
    path('buy_cod/<str:order_number>/<int:id>/', views.buy_cash_on_delivery, name='buy_cod'),
    path('buy_pay_success/', views.paypal_success, name="paypal_success"),

    

    

]