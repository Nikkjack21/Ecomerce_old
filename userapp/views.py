
from email import message
import random
from turtle import home
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from store.models import Product
from category.models import Category
from accounts.models import Account
from django.contrib import messages
from django.contrib.auth.models import User
from twilio.rest import Client
from django.contrib import auth
from django.contrib.auth.decorators import login_required


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
            auth_token      = '5957d8a798d02d9a9200e3c62e8bf89b'

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
        user      = Account.objects.get(phone_number = 8089758357)
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
                if Account.objects.filter(email=email).exists():
                    messages.info(request, "Email already taken")   
                    return redirect(signup)

                else:
                    myuser = Account.objects.create_user(first_name, last_name, username, email, password)
                    myuser.phone_number = phone_number
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
        messages.info(request, 'You have logged out')
        print("GETTING LOGGED OUT")
        return redirect(index)
    




def p_view(request, category_slug=None):
    categories         = None
    products           = None

    if category_slug   != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products   = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    context = {
            'products' : products,
    }

    return render(request, 'user/products.html', context)


# def product_details(request, category_slug, product_slug ):
#     return render(request,'user/product_details.html')
   

def p_details(request):
    return render(request,'user/product_detail.html')
