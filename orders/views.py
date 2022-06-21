from operator import gt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cartapp.models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist
from .forms import Orderform
from store.models import Product
from .models import Order, OrderProduct, Payment, RazorPay
from accounts.models import UserProfile
import datetime
from cartapp.views import _cart_id
import json
import razorpay
from django.conf import settings
from cartapp.views import offer_check_function




# Create your views here.
def payment(request):
    body            = json.loads(request.body)
    order           = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    print(order)
    print(body)
    #paypal tranasactions
    payment = Payment(
        user                = request.user,
        payment_id          = body['transID'],
        payment_method      = body['payment_method'],
        amount_paid         =  order.order_total,
        status              = body['status'],
        
    )
    payment.save()
    order.payment        = payment
    order.is_ordered     = True
    order.save()    


    CartItem.objects.filter(user=request.user).delete()
    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
    return render(request, 'orders/payments.html')





def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart   = Cart.objects.get(cart_id=_cart_id(request))
    cart_itemss   = CartItem.objects.filter(cart=cart, is_active=True,)
    
 
    


    grand_total=0
    tax=0
  
    for cart_item in cart_itemss:
        new_price = offer_check_function(cart_item)
        total += (new_price * cart_item.quantity)
        # total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100 
    grand_total =  total +tax
    # print(grand_total)
    
    val  = request.POST.get('selection')
    # print(val)

    if request.method == "POST":
        if val == 'typeadr':
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
                adrs            = UserProfile.objects.filter(user=request.user)
                
                context={
                    'order_data':order_data,
                    'cart_itemss': cart_itemss,
                    'cart_item': cart_item,
                    'total':total,
                    'tax': tax,
                    'grand_total': grand_total,
                    'adrs': adrs,

                }
                print(order_data.phone)

                print("SUCCESS")
                return render(request, 'orders/payments.html', context)
        else:
            add  = UserProfile.objects.get(id=val, user=request.user)
            a = add.state
            # print(add)
            data                        = Order()
            data.user                   = request.user
            data.first_name             = request.user.first_name
            data.last_name              = request.user.last_name
            data.phone                  = request.user.phone_number
            data.email                  = request.user.email
            data.address_line_1         = add.address_line_1
            data.address_line_2         = add.address_line_2
            data.country                = add.country
            data.state                  = add.state
            data.city                   = add.city

            data.order_total            = grand_total
            data.tax                    = tax
        
            data.ip                     = request.META.get('REMOTE_ADDR')
            data.save()


            order_number = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
            data.order_number = order_number
            data.save()

            order_data      = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
            adrs            = UserProfile.objects.filter(user=request.user)
            context={
                'order_data':order_data,
                'cart_itemss': cart_itemss,
                'total':total,
                'tax': tax,
                'grand_total': grand_total,
                'adrs': adrs

            }
            
            print(order_data.order_number)
            print("SUCCESS")
            return render(request, 'orders/payments.html', context)

    else:
        print(order_data.order_number)
        adrs  = UserProfile.objects.filter(user=request.user)
     
        context = {
            'adrs': adrs
        }
        return render(request, 'check/checkout.html', context)




def order_complete(request):
    
    order_number            = request.GET.get('order_number')
    transID                 = request.GET.get('payment_id')
   
    try:
        order     = Order.objects.get(order_number = order_number, is_ordered = True)
        
        payment   = Payment.objects.get(payment_id = transID)
        context = {
            'order': order,
            'order_number': order_number,
            'transID':payment.payment_id,
            'payment': payment,

        }
        return render(request, 'orders/success.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')





def razor_pay(request):
        cart   = Cart.objects.get(cart_id=_cart_id(request))
        cart_itemss   = CartItem.objects.filter(cart=cart, is_active=True,)
        
    
        


        grand_total=0
        tax=0
    
        for cart_item in cart_itemss:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100 
        grand_total =  total +tax

        
        razorpay_client = razorpay.Client(
        auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        currency = 'INR'
        amount = grand_total

        #create order
        razorpay_order = razorpay_client.order.create(  {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"})
        # order id of newly created order.
    
        razorpay_order_id = razorpay_order['id']
        callback_url = 'http://127.0.0.1:8000/orders/razor_success/'   
    
        # we need to pass these details to frontend.
        cart_item    = CartItem.objects.filter(user=request.user)
        
        order_data      = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
        context = {
        'razorpay_order_id' : razorpay_order_id,
        'razorpay_merchant_key' : settings.RAZOR_KEY_ID,
        'razorpay_amount' : amount,
        'currency' : currency ,
        'callback_url' : callback_url,
        
        'order_data':order_data,
        
        'cart_item':cart_item,

        }
        razor_model = RazorPay()
        razor_model.order = order_data
        razor_model.razor_pay = razorpay_order_id
        razor_model.save()
        pass










# def cash_on_delivery(request):
#     user = request.user
#     order_id = request.session.get('order_id')
#     print(order_id)
 
#     order = Order.objects.get(order_number = order_id)
#     cart_items = CartItem.objects.filter(user=user)
        
#     payment = Payment()
#     payment.user = user
#     payment.payment_id = order_id
#     payment.payment_method = 'COD'
#     payment.amount_paid=order.order_total
#     print("111111111")
 
#     payment.status = 'Pending'
#     payment.save()
#     order.payment=payment
#     order.is_ordered =True
#     order.save()

#     return render(request,'orders/success.html', {'order':order, 'cart_items': cart_items})


# def cash_on_delivery(request,order_number):
#     current_user = request.user
#     order= Order.objects.get(order_number=order_number)
#     print(order)

#     #transaction details store
#     payment = Payment()
#     payment.user= current_user
#     payment.payment_id = ''
#     payment.payment_method = 'Cash on delivery'
#     payment.amount_paid = ''
#     payment.status = 'Pending'
#     payment.save()
#     print(payment.payment_method)
    
#     order.payment=payment
#     order.save()
    # CartItem.objects.filter(user=request.user).delete()

#     return render(request,'orders/success.html', {'order':order})