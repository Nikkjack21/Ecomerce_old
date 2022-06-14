from django.urls import path
from .import views
urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('payments/', views.payment, name='payments'),
    path('cod/',views.cash_on_delivery,name='cash_on_delivery'),
    

]