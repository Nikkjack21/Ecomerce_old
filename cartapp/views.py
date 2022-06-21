
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from accounts.models import UserProfile
from store.models import Product
from category.models import Category
from .models import Cart, CartItem, ProductOffer, CategoryOffer
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.



def offer_check_function(item):
    product = Product.objects.get(product_name=item)
    print(product)
    print("CART_ITEM IS GOT")
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

    try:
        cart_item   = CartItem.objects.get(product=product, cart=cart, user=request.user)
        cart_item.quantity += 1   
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item   = CartItem.objects.create(
            user   = request.user,
            product  = product,
            quantity  = 1,
            cart  = cart
        )
        cart_item.save()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    
    tax=0
    grand_total=0
    try:
        cart   = Cart.objects.get(cart_id=_cart_id(request))
        cart_items   = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            new_price = offer_check_function(cart_item)
            total += (new_price * cart_item.quantity)
            # total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total  = total + tax
    except ObjectDoesNotExist:
      pass
    products  = Product.objects.all().filter(is_available=True)

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
    cart     = Cart.objects.get(cart_id=_cart_id(request))
    product  = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart  = Cart.objects.get(cart_id=_cart_id(request))
    product  = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def checkout(request, total=0, quantity=0, cart_items=None):
    tax=0
    grand_total=0
    profile  = UserProfile.objects.filter(user=request.user)
    print(profile)
    try:
        cart   = Cart.objects.get(cart_id=_cart_id(request))
        cart_items   = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            new_price = offer_check_function(cart_item)
            print(new_price)
            total += (new_price * cart_item.quantity)
            # total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total  = total + tax
    except:
       pass
       
    context ={
     
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'profile':profile,
        
    }
    return render(request, 'check/checkout.html', context)


    