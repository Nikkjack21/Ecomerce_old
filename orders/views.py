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
from django.views.decorators.csrf import csrf_exempt



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
    order.payment           = payment
    order.is_ordered        = True
    order.save()    


    cart_item = CartItem.objects.filter(user=request.user)
    
    
    #taking order_id to show the invoice

    
   
    for item in cart_item:
       
        OrderProduct.objects.create(
        order = order,
        product = item.product,
        user = request.user,
        quantity = item.quantity,
        product_price = item.product.price,
        payment = payment,
        ordered = True,
        )
    #decrease the product quantity from product
    orderproduct = Product.objects.filter(id=item.product_id).first()
    orderproduct.stock = orderproduct.stock-item.quantity
    orderproduct.save() 



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
    
 
    
    global order_data
    global grand_total
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


        # authorize razorpay client with API Keys.
           
           
            razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            currency = 'INR'
            amount = grand_total

            #create order
            razorpay_order = razorpay_client.order.create(  {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"})
            # order id of newly created order.
        
            razorpay_order_id = razorpay_order['id']
            callback_url = 'http://127.0.0.1:8000/orders/razor_success/'   

            context={
                'order_data':order_data,
                'cart_itemss': cart_itemss,
                'total':total,
                'tax': tax,
                'grand_total': grand_total,
                'adrs': adrs,
                'callback_url' : callback_url,
                'razorpay_order_id' : razorpay_order_id,
                'razorpay_merchant_key' : settings.RAZORPAY_KEY_ID,
                'razorpay_amount' : amount,
                'currency' : currency ,

            }
            razor_model =RazorPay()
            razor_model.order = order_data
            razor_model.razor_pay = razorpay_order_id
            razor_model.save()
            
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
        ordered_products    = OrderProduct.objects.filter(order_id = order.id)
        payment   = Payment.objects.get(payment_id = transID)
        context = {
            'order': order,
            'order_number': order_number,
            'transID':payment.payment_id,
            'payment': payment,
            'ordered_products': ordered_products,

        }
        return render(request, 'orders/success.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')












def cash_on_delivery(request,order_number):
    total =0
    quantity =0
    cart   = Cart.objects.get(cart_id=_cart_id(request))
    cart_itemss   = CartItem.objects.filter(cart=cart, is_active=True,)
    
    for cart_item in cart_itemss:
        new_price = offer_check_function(cart_item)
        total += (new_price * cart_item.quantity)
        # total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    current_user = request.user
    order= Order.objects.get(order_number=order_number)
    print(order)

    #transaction details store
    payment = Payment()
    payment.user= current_user
    payment.payment_id = ''
    payment.payment_method = 'Cash on delivery'
    payment.amount_paid = ''
    payment.status = 'Pending'
    payment.save()
    print(payment.payment_method)
    
    order.payment=payment
    order.is_ordered  = True
    order.save()

    cart_item = CartItem.objects.filter(user=current_user)
    
    
    #taking order_id to show the invoice

    
   
    for item in cart_item:
       
        OrderProduct.objects.create(
        order = order,
        product = item.product,
        user = current_user,
        quantity = item.quantity,
        product_price = item.product.price,
        payment = payment,
        ordered = True,
        )


    #decrease the product quantity from product
    orderproduct = Product.objects.filter(id=item.product_id).first()
    orderproduct.stock = orderproduct.stock-item.quantity
    orderproduct.save()
    CartItem.objects.filter(user=request.user).delete()

    order = Order.objects.get(order_number = order_number )
    order_product = OrderProduct.objects.filter(order=order)
    transID = OrderProduct.objects.filter(order=order).first()
    context = {
        'order':order,
        'order_product':order_product,
        'transID':transID,
        'cart_itemss': cart_itemss,
        'total': total,
    }

    return render(request,'orders/cod_success.html', context)






@csrf_exempt
def razor_success(request):
    print('Entering razor Viewwwwwww')
    transID = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')
    current_user = request.user

        #transaction details store

    razor = RazorPay.objects.get(razor_pay=razorpay_order_id)
    order = Order.objects.get(order_number = razor)
    print('razor success page')
    payment = Payment()
    payment.user= request.user
    payment.payment_id = transID
    payment.payment_method = "Razorpapy"
    payment.amount_paid = order.order_total
    payment.status = "Completed"
    payment.save()

    order.payment=payment
    order.is_ordered = True
    order.save()

    cart_item = CartItem.objects.filter(user=current_user)
    
    
    # Invoice Generating by using order_id

    
   
    for item in cart_item:
       
        OrderProduct.objects.create(
        order = order,
        product = item.product,
        user = current_user,
        quantity = item.quantity,
        product_price = item.product.price,
        payment = payment,
        ordered = True,
        )

        #decreasing products from stock after order

        orderproduct = Product.objects.filter(id=item.product_id).first()
        orderproduct.stock = orderproduct.stock-item.quantity
        orderproduct.save()

        #deleting Cart items after order


        CartItem.objects.filter(user=current_user).delete()


    order = Order.objects.get(order_number = razor )
    order_product = OrderProduct.objects.filter(order=order)
    transID = OrderProduct.objects.filter(order=order).first()
    context = {
        'order':order,
        'order_product':order_product,
        'transID':transID
    }

    return render(request,'orders/success.html', context)




























    
# def razor_pay(request):
#         razorpay_client = razorpay.Client(
#         auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

#         currency = 'INR'
#         amount = grand_total
#         print(grand_total)

#         #create order
#         razorpay_order = razorpay_client.order.create(  {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"})
#         # order id of newly created order.
    
#         razorpay_order_id = razorpay_order['id']
#         callback_url = 'http://127.0.0.1:8000/orders/razor_success/'   
    
#         # we need to pass these details to frontend.
#         context = {
#         'razorpay_order_id' : razorpay_order_id,
#         'razorpay_merchant_key' : settings.RAZOR_KEY_ID,
#         'razorpay_amount' : amount,
#         'currency' : currency ,
#         'callback_url' : callback_url,


#         }
#         razor_model =RazorPay()
#         razor_model.order = order_data
#         print(order_data)
#         razor_model.razor_pay = razorpay_order_id
#         razor_model.save()
#         print('razor Success')
#         transID = request.POST.get('razorpay_payment_id')
#         razorpay_order_id = request.POST.get('razorpay_order_id')
#         signature = request.POST.get('razorpay_signature')
#         current_user = request.user
#                 #transaction details store
#         razor = RazorPay.objects.get(razor_pay=razorpay_order_id)
#         order = Order.objects.get(order_number = razor)
#         print('razor success page')
#         payment = Payment()
#         payment.user= request.user
#         payment.payment_id = transID
#         payment.payment_method = "Razorpapy"
#         payment.amount_paid = order.order_total
#         payment.status = "Completed"
#         payment.save()

#         order.payment=payment
#         order.save()



        
#         cart_item = CartItem.objects.filter(user=current_user)
#         for item in cart_item:
       
#             OrderProduct.objects.create(
#             order = order,
#             product = item.product,
#             user = current_user,
#             quantity = item.quantity,
#             product_price = item.product.price,
#             payment = payment,
#             ordered = True,
#             )
    
#         #decrease the product quantity from product
#         orderproduct = Product.objects.filter(id=item.product_id).first()
#         orderproduct.stock = orderproduct.stock-item.quantity
#         orderproduct.save()
#         #delete cart item from usercart after ordered
#         CartItem.objects.filter(user=current_user).delete()

#         order = Order.objects.get(order_number = razor )
#         order_product = OrderProduct.objects.filter(order=order)
#         transID = OrderProduct.objects.filter(order=order).first()
#         context = {
#             'order':order,
#             'order_product':order_product,
#             'transID':transID
#         }
#         return render(request,'orders/success.html', context)


