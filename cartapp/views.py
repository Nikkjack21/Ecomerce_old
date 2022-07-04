
import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from accounts.models import Address, UserProfile
from store.models import Product
from category.models import Category
from .models import Cart, CartItem, Coupon, CouponUsedUser, ProductOffer, CategoryOffer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .forms import CouponApplyForm
from django.contrib import messages


# Create your views here.



def offer_check_function(item):
    product = Product.objects.get(product_name=item)
  
    print("OFFER CHECK ACTIVE")
    if ProductOffer.objects.filter(product=product,active=True).exists():
        if product.pro_offer:
            off_total = product.price - product.price*product.pro_offer.discount/100
    else:
        off_total = product.price
        print(off_total)
    return off_total






def _cart_id(request):
    cart      = request.session.session_key
    if not cart:
        cart  = request.session.create()
    return cart



def add_cart(request, product_id):
   
    product         = Product.objects.get(id=product_id)
    try:
        cart        = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart        = Cart.objects.create(
            cart_id = _cart_id(request) 
        )
    
    cart.save()
    if request.user.is_authenticated:
        try:
            cart_item   = CartItem.objects.get(product=product, user=request.user)
            cart_item.quantity += 1   
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item   = CartItem.objects.create(
                user=request.user,
                product  = product,
                quantity  = 1,
                cart  = cart
            )
            cart_item.save()
        return redirect('cart')
    else:     
        try:
            cart_item   = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1   
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item   = CartItem.objects.create(
            
                product  = product,
                quantity  = 1,
                cart  = cart
            )
            cart_item.save()
        return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    products  = Product.objects.all().filter(is_available=True)
    try:
        print('ENTERING TRY BLOCCK')
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            print("USER IS REQUESTED")
            cart_items   = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            print("USER IS NOT REQUESTED")          
            cart   = Cart.objects.get(cart_id=_cart_id(request))
            cart_items   = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            new_price = offer_check_function(cart_item)
            total += (new_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total  = total + tax
        
    except ObjectDoesNotExist:
        pass
    

    context ={
      
        'products': products,
       
        'total': total,
        'quantity': quantity,
       
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        
    }
    

    return render(request, 'shop-shopping-cart.html', context)


def remove_cart(request, product_id):

    product  = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user) 
    else:      
        cart     = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):

    product  = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user) 
    else:    
        cart  = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


    

@login_required(login_url='signin')
def checkout(request, total=0, quantity=0, cart_items=None):

    tax=0
    grand_total=0
    profile  = Address.objects.filter(user=request.user).order_by('id')
    print(profile)

    try:
        if request.user.is_authenticated:
            print('CHECKOUT USER REQUEST')
            cart_items   = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart   = Cart.objects.get(cart_id=_cart_id(request))
            cart_items   = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            new_price = offer_check_function(cart_item)
            print(new_price)
            total += (new_price * cart_item.quantity)
        
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total  = total + tax
        print(grand_total)
    except:
       pass
    coupon_apply_form = CouponApplyForm()
   
    if request.session.get('coupon_id'):
        coupon_id = request.session.get('coupon_id')
        print(coupon_id)
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if CouponUsedUser.objects.filter(coupon=coupon,user=request.user).exists():
                print('Coupon already used')
                final_price = grand_total
                messages.successs(request,'Coupon already used')
            else:
                deduction = coupon.discount_amount(grand_total)
                final_price = grand_total-deduction
                print('Coupon Applied')

                print(final_price)
        except:
            pass
        
    else:
        final_price = grand_total
       



    context ={
        
        'total': total,
        'final_price': final_price,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'profile':profile,
        'coupon_apply_form':coupon_apply_form,
        
    }
    return render(request, 'check/checkout.html', context)


    



def buy_now(request, id):
    try:
        print('ENTERED BUY NOW')
       
        profile  = Address.objects.filter(user=request.user).order_by('id')
        total=0
        tax = 0
        grand_total = 0
        cart_items = Product.objects.get(id=id)
        total = (cart_items.price * 1)
        tax = (2 * total)/100
        grand_total = tax+total
        request.session['cart_items.id']  = cart_items.id
    except:
        pass
    context ={
       
        'cart_item': cart_items,
        'totals': total,
        'taxs': tax,
        'grand_totals': grand_total, 
        'profile':profile, 
    }


    return render(request, 'buy/buy_checkout.html', context)








def buy_add_address(request):
    adrs     = Address()
    cartitems = request.session['cart_items.id']
    print('entering session')
    print(cartitems)
    if request.method == "POST":
        adrs.user               = request.user
        adrs.name               = request.POST.get('name')
        adrs.phone              = request.POST.get('phone')
        adrs.email              = request.POST.get('email')
        adrs.address_line       = request.POST.get('address_line_1')
        adrs.pincode            = request.POST.get('pincode')
        adrs.city               = request.POST.get('city')
        adrs.state              = request.POST.get('state')
        adrs.country            = request.POST.get('country')
        adrs.save()
        messages.success(request, "Address Added")
        return HttpResponseRedirect(reverse('buy_now_checkout', args=(cartitems,)))
    context={
        'adrs':adrs,
        
      
    }   
    return render(request, 'user/add_address.html', context)















def coupon_apply(request):
    now = timezone.now()
    
    form = CouponApplyForm(request.POST)
    print(now)
    if form.is_valid():
        
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
            request.session['coupon_id']=coupon.id
            print('Coupon session')
            return redirect('checkout')
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            print('Coupon session not working')
            return redirect('checkout')