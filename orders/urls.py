from django.urls import path
from .import views
urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('payments/', views.payment, name='payments'),
    path('cod/<str:order_number>/',views.cash_on_delivery,name='cash_on_delivery'),
    path('success/', views.order_complete, name='success'),
    path('razor_success/', views.razor_success, name='razor_success'),
    path('buy_now_place_order/<int:id>', views.buy_now_place_order, name="buy_now_place_order"),
    path('buy_now_payments/', views.buy_now_payment, name='buy_now_pay'),
    path('buy_cod/<int:id>/<str:order_number>/', views.buy_cash_on_delivery, name='buy_cod'),
    

    

]