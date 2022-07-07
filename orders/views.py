from operator import gt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cartapp.models import CartItem, Cart, Coupon, CouponUsedUser
from django.core.exceptions import ObjectDoesNotExist
from .forms import Orderform
from store.models import Product
from .models import Order, OrderProduct, Payment, RazorPay
from accounts.models import Address, UserProfile
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
    count = 0
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
    if request.session.get('coupon_id'):
        coupon_id = request.session.get('coupon_id')
        del request.session['coupon_id']
        coupon = Coupon.objects.get(id=coupon_id)
        coupon_used = CouponUsedUser.objects.create(
        coupon = coupon,
        user=request.user,
        count = count+ 1
                    )
        coupon_used.save()
    else:
        None
    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    
    }
    return JsonResponse(data)
    return render(request, 'orders/payments.html')





def place_order(request, total=0, quantity=0, coups=None, coupon=None):
    
    current_user = request.user
    if request.user.is_authenticated:
        cart_itemss   = CartItem.objects.filter(user=current_user, is_active=True,)
    else:
        cart   = Cart.objects.get(cart_id=_cart_id(request))
        cart_itemss   = CartItem.objects.filter(cart=cart, is_active=True,)
        
 
    
    global order_data
    final_price=0
    deduction=0
  
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
    print(val)

    if request.method == "POST":
        if val == 'typeadr':
            form         = Orderform(request.POST)
            if form.is_valid():
                data                        = Order()
                data.user                   = current_user
                data.first_name             = form.cleaned_data['name']
          
                data.phone                  = form.cleaned_data['phone']
                data.email                  = form.cleaned_data['email']
                data.address_line_1         = form.cleaned_data['address_line_1']
              
                data.country                = form.cleaned_data['country']
                data.state                  = form.cleaned_data['state']
                data.city                   = form.cleaned_data['city']

                data.order_total            = grand_total
                data.tax                    = tax
            
                data.ip                     = request.META.get('REMOTE_ADDR')
                data.save()

              

                order_number = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
                data.order_number = order_number
                request.session['order_id'] = data.order_number
                data.save()


                order_data      = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                adrs            = Address.objects.filter(user=request.user)
                if request.session:
                    coupon_id = request.session.get('coupon_id')
                    print(coupon_id)
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    coups  = CouponUsedUser.objects.filter(coupon=coupon,user=request.user).exists()
                    if coups:
                        print('ENTERING ORDER IF COUPS')
                        pass
                    else:
                        print('ENTERING ORDER ELSE COUPS')
                        deduction = coupon.discount_amount(total)
                        final_price = total-deduction
                        print(final_price)
                        grand_total = tax + final_price
                        print(grand_total)
                        print('SHOWNG APPLIED COUPON GRAND TOTAL')
                    
                except:
                    pass
            
                else:
            


                    grand_total = grand_total
                data.save()
                
                context={
                    'order_data':order_data,
                    'cart_itemss': cart_itemss,
                    'cart_item': cart_item,
                    'total':total,
                    'tax': tax,
                    'grand_total': grand_total,
                    'adrs': adrs,
                    'final_price': final_price,
                    'deduction':deduction,
                    'coupon': coupon,
                    'coups': coups,
                    'coups':coups,
                }
                print(order_data.phone)

                print("SUCCESS")
                return render(request, 'orders/payments.html', context)
        else:
            add  = Address.objects.get(id=val, user=request.user)
            a = add.state
            # print(add)
            data                        = Order()
            data.user                   = request.user
            data.first_name             = add.name
         
            data.phone                  = add.phone
            data.email                  = add.email
            data.address_line_1         = add.address_line
        
            data.country                = add.country
            data.state                  = add.state
            data.city                   = add.city

            data.order_total            = grand_total
            data.tax                    = tax
        
            data.ip                     = request.META.get('REMOTE_ADDR')
            data.save()


            order_number = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
            data.order_number = order_number
            request.session['data_id'] = data.order_number

            data.save()

            order_data      = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
            adrs            = Address.objects.filter(user=request.user)
            if request.session:
                coupon_id = request.session.get('coupon_id')
                print(coupon_id)
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                coups  = CouponUsedUser.objects.filter(coupon=coupon,user=request.user).exists()
                if coups:
                    print('ENTERING ORDER IF COUPS')
                    pass
                else:
                    print('ENTERING ORDER ELSE COUPS')
                    deduction = coupon.discount_amount(total)
                    final_price = total-deduction
                    print(final_price)
                    grand_total = tax + final_price
                    print(grand_total)
                    print('SHOWNG APPLIED COUPON GRAND TOTAL')
            
            except:
                pass
        
            else:
        


                grand_total = grand_total



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
                'final_price': final_price,
                'deduction':deduction,
                'coupon': coupon,
                'coups': coups,
                'coups': coups,

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
        adrs  = Address.objects.filter(user=request.user)
     
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
    coupon = None
    if request.user.is_authenticated:
        cart_itemss   = CartItem.objects.filter(user=request.user, is_active=True,)
    else:
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
    count =0
    if request.session.get('coupon_id'):
        coupon_id = request.session.get('coupon_id')
        del request.session['coupon_id']
        coupon = Coupon.objects.get(id=coupon_id)
        coupon_used = CouponUsedUser.objects.create(
        coupon = coupon,
        user=request.user,
        count = count+ 1
                    )
        coupon_used.save()
    context = {
        'order':order,
        'order_product':order_product,
        'transID':transID,
        'cart_itemss': cart_itemss,
        'total': total,
        'coupon':coupon,
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

    return render(request,'orders/razor_success.html', context)



# def buy_now_payment(request,id):
#     cart_items   = Product.objects.get(id=id)
#     return render(request, 'buy/buy_now_payments.html', {'cart_items':cart_items})


def buy_now_place_order(request, id, deduction=0, final_price=0,coupon=None):

    cart_itemss     = Product.objects.get(id=id)
    total           = 0
    tax             = 0
    grand_total     = 0
    new_price       = offer_check_function(cart_itemss)
    total           = (new_price * 1)
    tax             = (2 * total)/100
    grand_total     = tax+total

    val             = request.POST.get('selection')
    print(val)

    if request.method == "POST":
        if val        == 'typeadr':
            form                   = Orderform(request.POST)
            if form.is_valid():
                data                        = Order()
                data.user                   = request.user
                data.first_name             = form.cleaned_data['name']

                data.phone                  = form.cleaned_data['phone']
                data.email                  = form.cleaned_data['email']
                data.address_line_1         = form.cleaned_data['address_line']
            
                data.country                = form.cleaned_data['country']
                data.state                  = form.cleaned_data['state']
                data.city                   = form.cleaned_data['city']

                data.order_total            = grand_total
                data.tax                    = tax

                data.save()
               
                order_number = str(int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
                data.order_number = order_number
                data.save()

                order_data      = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
                print(order_data)
                adrs            = Address.objects.filter(user=request.user)
                if request.session:
                    coupon_id = request.session.get('coupon_id')
                    print(coupon_id)
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    deduction = coupon.discount_amount(total)
                    final_price = total-deduction
                    print(final_price)
                    grand_total = tax + final_price
                    print(grand_total)
                    print('SHOWNG APPLIED COUPON GRAND TOTAL')
                    
                except:
                    pass
            
                else:
            


                    grand_total = grand_total
                    print(grand_total)


                context={
                        'order_data':order_data,
                        'cart_items': cart_itemss,
                        'total':total,
                   
                        'tax': tax,
                        'grand_total': grand_total,
                        'adrs': adrs,
                        'final_price': final_price,
                        'deduction':deduction,
                        'coupon': coupon,

                        }
                print('SUCCESSFULLY WORKKING')
                return render(request, 'buy/buy_now_payments.html', context)
        else:
            add  = Address.objects.get(id=val, user=request.user)
            a = add.state
            # print(add)
            data                        = Order()
            data.user                   = request.user
            data.first_name             = add.name
         
            data.phone                  = add.phone
            data.email                  = add.email
            data.address_line_1         = add.address_line
        
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
            adrs            = Address.objects.filter(user=request.user)
            
            if request.session:
                coupon_id = request.session.get('coupon_id')
                print(coupon_id)
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                deduction = coupon.discount_amount(total)
                final_price = total-deduction
                print(final_price)
                grand_total = tax + final_price
                print(grand_total)
                print('SHOWNG APPLIED COUPON GRAND TOTAL')
                
            except:
                pass
        
            else:
        


                grand_total = grand_total
                print(grand_total)

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
                'cart_items': cart_itemss,
                'total':total,
                'tax': tax,
                'grand_total': grand_total,
                'adrs': adrs,
                'callback_url' : callback_url,
                'razorpay_order_id' : razorpay_order_id,
                'razorpay_merchant_key' : settings.RAZORPAY_KEY_ID,
                'razorpay_amount' : amount,
                'currency' : currency ,
                'id': id,
                'final_price': final_price,
                'deduction':deduction,
                'coupon': coupon,

            }
            razor_model =RazorPay()
            razor_model.order = order_data
            razor_model.razor_pay = razorpay_order_id
            razor_model.save()
            
            print(order_data.order_number)
            print("ELSE CONDITION SUCCESS")
            return render(request, 'buy/buy_now_payments.html', context)

    else:
        print(order_data.order_number)
        adrs  = Address.objects.filter(user=request.user)
     
        context = {
            'adrs': adrs
        }
        print('MAIN ELSE SUCCESSFULLY WORKKING')
    return render(request, 'buy/buy_checkout.html', context)



def buy_paypal(request,id):
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


    item = Product.objects.get(id=id)
    print(item.id)


    
    OrderProduct.objects.create(
    order = order,
    product = item,
    user = request.user,
    quantity = 1,
    product_price = item.price,
    payment = payment,
    ordered = True,
    )
    #decrease the product quantity from product
    orderproduct = Product.objects.filter(id=item.id).first()
    orderproduct.stock = orderproduct.stock-1
    orderproduct.save() 



    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
        
    }
    return JsonResponse(data)



@csrf_exempt
def buy_razor_success(request,id):
    print('Entering razor buy Now Viewwwwwww')
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

    item = Product.objects.get(id=id)
    
    
    # Invoice Generating by using order_id

    
    
    OrderProduct.objects.create(
    order = order,
    product = item.product,
    user = current_user,
    quantity = 1,
    product_price = item.price,
    payment = payment,
    ordered = True,
    )

    #decreasing products from stock after order

    orderproduct = Product.objects.filter(id=item.id).first()
    orderproduct.stock = orderproduct.stock-1
    orderproduct.save()

    #deleting Cart items after order


     


    order = Order.objects.get(order_number = razor )
    order_product = OrderProduct.objects.filter(order=order)
    transID = OrderProduct.objects.filter(order=order).first()
    context = {
        'order':order,
        'order_product':order_product,
        'transID':transID
    }

    return render(request,'buy/razor_success_buy.html', context)






def buy_cash_on_delivery(request,id,order_number):
    total =0
    quantity =1
    current_user = request.user
    order= Order.objects.get(order_number=order_number)
    print(order)

    #transaction details store
    payment = Payment()
    payment.user= current_user
    payment.payment_id = ''
    payment.payment_method = 'Cash on delivery'
    payment.amount_paid = ''
    payment.status = 'Order Confirmed'
    payment.save()
    print(payment.payment_method)
    
    order.payment=payment
    order.is_ordered  = True
    order.save()

    item  = Product.objects.get(id=id)
    
    
    #taking order_id to show the invoice


    
    OrderProduct.objects.create(
    order = order,
    product = item,
    user = current_user,
    quantity = 1,
    product_price = item.price,
    payment = payment,
    ordered = True,
    )


    #decrease the product quantity from product
    orderproduct = Product.objects.filter(id=item.id).first()
    orderproduct.stock = orderproduct.stock-quantity
    orderproduct.save()


    order = Order.objects.get(order_number = order_number )
    order_product = OrderProduct.objects.filter(order=order)
    transID = OrderProduct.objects.filter(order=order).first()
    context = {
        'order':order,
        'order_product':order_product,
        'transID':transID,
        'cart_items': item,
        'total': total,
    }

    return render(request,'buy/cod_success_buy.html', context)





# def paypal_success(request):
#     order_number            = request.GET.get('order_number')
#     transID                 = request.GET.get('payment_id')
   
#     try:
#         order     = Order.objects.get(order_number = order_number, is_ordered = True)
#         ordered_products    = OrderProduct.objects.filter(order_id = order.id)
#         payment   = Payment.objects.get(payment_id = transID)
#         context = {
#             'order': order,
#             'order_number': order_number,
#             'transID':payment.payment_id,
#             'payment': payment,
#             'ordered_products': ordered_products,

#         }
#         return render(request, 'buy/paypal_success.html', context)
#     except (Payment.DoesNotExist, Order.DoesNotExist):
#         return redirect('index')