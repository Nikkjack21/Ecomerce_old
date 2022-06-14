from operator import gt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cartapp.models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist
from .forms import Orderform
from store.models import Product
from .models import Order, OrderProduct, Payment
import datetime
from cartapp.views import _cart_id
# Create your views here.
def payment(request):
    return render(request, 'orders/payments.html')

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart   = Cart.objects.get(cart_id=_cart_id(request))
    cart_itemss   = CartItem.objects.filter(cart=cart, is_active=True,)
    
    print(cart_itemss)
    


    grand_total=0
    tax=0
  
    for cart_item in cart_itemss:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100 
    grand_total =  total +tax
    print(grand_total)
    
    if request.method == "POST":
        form         = Orderform(request.POST)
        if form.is_valid():
            data                        = Order()
            data.user                   = current_user
            data.first_name             = form.cleaned_data['first_name']
            data.last_name              = form.cleaned_data['last_name']
            data.phone                  = form.cleaned_data['phone']
            data.email                  = form.cleaned_data['email']
            data.address_line_1         = form.cleaned_data['address_line_1']
            data.address_line_2         = form.cleaned_data['address_line_2']
            data.country                = form.cleaned_data['country']
            data.state                  = form.cleaned_data['state']
            data.city                   = form.cleaned_data['city']

            data.order_total            = grand_total
            data.tax                    = tax
          
            data.ip                     = request.META.get('REMOTE_ADDR')
            data.save()

            cart_item    = CartItem.objects.filter(user=current_user)

            order_number = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
            data.order_number = order_number
            data.save()

            order_data      = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            context={
                'order_data':order_data,
                'cart_itemss': cart_itemss,
                'cart_item': cart_item,
                'total':total,
                'tax': tax,
                'grand_total': grand_total

            }
            print(order_data.phone)

            print("SUCCESS")
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')



def cash_on_delivery(request):


    return render(request,'orders/success.html')


