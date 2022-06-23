
from email import message
from multiprocessing import context
import random
from turtle import home
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from cartapp.models import CartItem, Cart
from orders.models import Order
from store.models import Product
from category.models import Category
from accounts.models import Account, UserProfile
from django.contrib import messages
from django.contrib.auth.models import User
from twilio.rest import Client
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cartapp.views import _cart_id
from django.http import HttpResponse
from accounts.forms import UserForm, UserProfileForm


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    products = Product.objects.all().filter(is_available=True)

    context = {
        'products' : products,
    }
   
    return render(request, 'user/shop-index.html', context)





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signin(request):
    if request.user.is_authenticated:
        return redirect(index)

    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)


            if user is not None:
                login(request, user)
                messages.success(request, 'You have succesfully logged in', )
                return redirect(index)

            else:
                messages.error(request, "Invalid Credentials")
                print('NOT ABLE TO SIGNIN')
                return redirect(signin)
        return render(request, 'reg/signin.html')


# OTP CODE BEGINS HERE----------------------------------------------------------------------

@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def otp(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        mobile      = '8089758357'
        phone_number = request.POST['phone_number']
        if mobile == phone_number:
            account_sid     = 'AC29ac10e058d302306bbbd63a523a0f15'
            auth_token      = '493bef2657652d28660c426702d59617'

            client      = Client(account_sid, auth_token)
            global otp
            otp         = str(random.randint(1000, 9999))
            message     = client.messages.create(
                to      ='+918089758357',
                from_    ='+1 850 789 7381',
                body    ='Your OTP code is'+ otp)
            messages.success(request, 'OTP has been sent to 8089758357')
            print('OTP SENT SUCCESSFULLY')
            return redirect(otpcode)
        else:
            messages.info(request, 'Invalid Mobile number')
            return redirect(otp)

    return render(request, 'reg/otplogin.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def otpcode(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        user      = Account.objects.get(phone_number=8089758357)
        otpvalue  = request.POST.get('otp')
        if otpvalue == otp:
            print('VALUE IS EQUAL')
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid OTP')
            print('ERROR ERROR')
            return redirect(otp)

    return render(request, 'reg/otpcode.html')


# OTP CODE ENDS HERE-----------------------------------------------------------------------------



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup(request):
    if request.user.is_authenticated:
        return redirect(index)
    if request.method == 'POST':
        first_name      = request.POST.get('first_name')
        last_name       = request.POST.get('last_name')
        email           = request.POST.get('email')
        username        = request.POST.get('username')
        phone_number    = request.POST.get('phone_number')
        password        = request.POST.get('password')
        password2       = request.POST.get('password2')

        if password == password2:
            if username=='' and email=='' and password=='':
                messages.info(request, "Fields cannot be blank")
                return redirect(signup)
            elif first_name =='' or last_name == '':
                messages.info(request, "Name field cannot be blank")
                return redirect(signup)
 
            else:
                if Account.objects.filter(username=username).exists():
                    messages.info(request, "Username already taken")
                    return redirect(signup)
                elif Account.objects.filter(email=email).exists():
                    messages.info(request, "Email already taken")   
                    return redirect(signup)

                else:
                    myuser = Account.objects.create_user(first_name, last_name, username, email, password)
                    myuser.phone_number = phone_number
                    myuser.save()

                    print('user created')
                    messages.success(request, "You have successfully created account ")
                    return redirect(signin)
                
        else:
            messages.error(request,"Passwords donot match")
            return redirect(signup)

    return render(request, 'reg/signup.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signout(request):

        logout(request)
        print("GETTING LOGGED OUT") 
        messages.info(request, 'You have logged out')
        return redirect(index)
    




def p_view(request, category_slug=None):
    categories         = None
    products           = None

    if category_slug   != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products        = Product.objects.filter(category=categories, is_available=True)
        paginator       = Paginator(products,3)
        page            = request.GET.get('page')
        paged_product   = paginator.get_page(page)
    else:
        products        = Product.objects.all().filter(is_available=True)
        paginator       = Paginator(products,3)
        page            = request.GET.get('page')
        paged_product   = paginator.get_page(page)

    context = {
            'products' : paged_product,
    }

    return render(request, 'user/products.html', context)


   

def p_details(request, category_slug, product_slug):
    try:
        single_product   = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart          = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart
    }
    return render(request,'user/product_detail.html', context)


def my_account(request):
    if request.user.is_authenticated:
        return render(request, 'user/myaccount.html')
    else:
        return redirect('signin')



@login_required(login_url='/signin/')
def changePassword(request):
    if request.method == 'POST':
        current_password    = request.POST['current_password']
        new_password        = request.POST['new_password']
        confirm_password    = request.POST['confirm_password']

        user                = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success        = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid password')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords donot match')
            return redirect('change_password')
    return render(request,'user/password.html')




def editProfile(request, id=id):
    if not request.user.is_authenticated:
        return redirect(signin)
    else:
        # userprofile     = get_object_or_404(UserProfile,user=request.user)
        userprofile     = UserProfile.objects.get(id=id)
        # userprofile     = UserProfile.objects.filter(id=id, user=request.user).first()
        
       
        if request.method == "POST":
            user_form           = UserForm(request.POST, instance=request.user)
            profile_form        = UserProfileForm(request.POST, request.FILES, instance=userprofile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Succesfully Updated")
                return redirect('edit_profile', id)
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=userprofile) 
    adr = UserProfile.objects.get(id=id)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'adr': adr,
    }
    return render(request, 'user/editpro.html', context)


def my_orders(request):
    user = request.user
    orders  = Order.objects.filter(user=user).order_by('-id')
    items = CartItem.objects.filter(user=user)
    
    
    print(user)
    print('Show items below')
    print(items)
    context ={
        'orders': orders,
        'items': items
    }
    return render(request, 'user/myorders.html', context)


def order_user_actions(request, id):
    order  = Order.objects.filter(id=id)
    order.update(status='Cancelled')
    return redirect('my_orders')




def user_address(request):
    address = UserProfile.objects.filter(user=request.user)
    context={
        'address': address
    }
    return render(request, 'user/user_address.html', context)


def add_address(request):
    adrs  = UserProfile()
    
    if request.method=="POST":
        adrs.user               = request.user
        # adrs.first_name         = request.POST.get('first_name')
        # adrs.last_name          = request.POST.get('last_name')
        # adrs.email              = request.POST.get('email')
        # adrs.phone_number       = request.POST.get('phone_number')
       
        adrs.address_line_1     = request.POST.get('address_line_1')
        adrs.address_line_2     = request.POST.get('address_line_2')
        adrs.city               = request.POST.get('city')
        adrs.state              = request.POST.get('state')
        adrs.country            = request.POST.get('country')
        adrs.save()
        messages.success(request, "Address Added")
        return redirect(add_address)
    context={
        'adrs':adrs
    }
    return render(request, 'user/add_address.html', context)







def verify_num(request):
    return render(request, 'reg/verification.html')