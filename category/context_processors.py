from cartapp.models import Cart, CartItem, ProductOffer
from cartapp.views import _cart_id, offer_check_function
from .models import MainCategory
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist



def menu_links(request):
    main_cat      = MainCategory.objects.all()
   

    return{'main_cat': main_cat}




def cart_count(request):

    try:
        tax=0
        total=0
        quantity=0
        cart_items = None
        grand_total=0
        if request.user.is_authenticated:
            print("USER IS REQUESTED")
            cart_items   = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
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
    return{'grand_total':grand_total, 'cart_items': cart_items}


