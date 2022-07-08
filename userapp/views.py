
from multiprocessing import context
import random
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from cartapp.models import CartItem, Cart
from orders.models import Order
from projectseven import settings
from store.models import Product
from category.models import Category, MainCategory
from accounts.models import Account, Address, UserProfile, Wallet
from django.contrib import messages
from django.contrib.auth.models import User
from twilio.rest import Client
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from cartapp.views import _cart_id, cart
from django.http import HttpResponse
from accounts.forms import UserForm, UserProfileForm




def index(request):
    products = Product.objects.all().filter(is_available=True)
    pop   = Product.objects.all().filter(is_available=True)[9:12]
    slider   = Product.objects.all().filter(is_available=True)[17:]
    return render(request, 'user/shop-index.html', {'products':products, 'pop':pop, 'slider': slider})





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
                try:
                    print("ENtering try BLock")
                    cart        = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists    = CartItem.objects.filter(cart=cart).exists()
                    print(is_cart_item_exists)
                    if is_cart_item_exists:
                        cart_items  = CartItem.objects.filter(cart=cart)
                        print(cart_items)

                        for cart_item in cart_items:
                            cart_item.user = user
                            print(cart_item.user)
                            cart_item.save()
                except:
                    print("ENtering Except BLock")
                    pass
                login(request, user)
                wall = Wallet.objects.filter(user=request.user).exists()
                print('wallet user exists')
                if not wall:
                    wall = Wallet.objects.create(user=request.user)
                    wall.save()
                    print('wallet created for user')

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
            auth_token      = settings.AUTH_TOKEN

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
        # phone_number    = request.POST.get('phone_number')
        password        = request.POST.get('password')
        password2       = request.POST.get('password2')
        s               = first_name
        refer           = s[:len(s)//2] + 'ZHEA' + "XYZ"

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
                    myuser.referral_code = refer
                    myuser.save()
                    user_name = myuser
                    context = { 
                        'user_name':user_name
                    }
                    #messages.success(request,'Welcome , Registered Succesfully !')
                    return render(request,'reg/verify.html',context)

                    print('user created')
                    messages.success(request, "You have successfully created account ")
                    return redirect(signin)
                
        else:
            messages.error(request,"Passwords donot match")
            return redirect(signup)

    return render(request, 'reg/signup.html')




def phone_verfiy(request):
    return render(request, 'reg/verify.html')


def phone_verification(request):
    user_name = request.GET.get('user_name')
    print(user_name)
    if request.method == 'POST':
        
        print("1")
        count =0
        phone_number = request.POST['phone_number']
        phone_no="+91" + phone_number
        for i in phone_number:
            count=count+1
        
        if count == 10 :
            print("0000")
            if Account.objects.filter(phone_number=phone_number).exists():
                user1= Account.objects.filter(username = user_name)
                user1.delete()
                messages.info(request,'number already exist ! !')
                return redirect('signup')
            else:
                # Your Account SID twilio
                account_sid = "AC29ac10e058d302306bbbd63a523a0f15"
                # Your Auth Token twilio
                auth_token  = settings.AUTH_TOKEN

                client = Client(account_sid, auth_token)
                verification = client.verify \
                        .services("VA38cc8734ac2db4a918b56a6bd98030c7") \
                        .verifications \
                        .create(to=phone_no,channel='sms')
                print("1234")
                
                context = {
                    'phone_number': phone_number,
                    'user_name':user_name,

                }
                return render (request, 'reg/verification.html',context)

        
        else :  
            print("6666")
            if Account.objects.filter(username = user_name).exists():
                user1= Account.objects.filter(username = user_name)
                user1.delete()
                messages.success(request,'entered phone number is not correct !')
                return redirect('signup')
           
            else : 
                messages.success(request,'entered phone number is not correct !')
                return redirect('signup')

    else : 
            print("3333336")

            messages.success(request,'Please enter correct phone number !')
            return redirect('signup')








def otp_verification(request,phone_number):
   
    user_name = request.GET.get('name')
    print(phone_number)
    print(user_name)
    phone_no = "+91" + str(phone_number)

    if request.method=='POST':

        otp_input =  request.POST['number']
        account_sid = "AC29ac10e058d302306bbbd63a523a0f15"
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        verification_check = client.verify \
                                .services("VA38cc8734ac2db4a918b56a6bd98030c7") \
                                .verification_checks \
                                .create(to= phone_no, code= otp_input)
           
        
        if verification_check.status == "approved":
            messages.success(request,"OTP verified successfully.")
            user = Account.objects.get(username=user_name)
            user.is_active = True   
            user.phone_number = phone_number        
            user.save()          
            messages.success(request,"registered successfully")
            return redirect ('signin')
        else:
            print("Entering else statementt")
            messages.success(request,"Invalid OTP")
            return redirect ('signup')

    else:
        return render (request, 'reg/verification.html')








@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signout(request):

        logout(request)
        
        print("GETTING LOGGED OUT") 
        messages.info(request, 'You have logged out')
        return redirect(index)



def pro_store(request, id):
    main_cat = MainCategory.objects.all()
    category  = Category.objects.get(id=id)
    print('ENTERED PRO STORE')

    if category is not None:
        products    = Product.objects.filter(category=category, is_available=True)
        print("PRO_STORE IS ACTUALYY WROKINGGGGGGGGGG")
    else:
        products   = Product.objects.all().filter(is_available=True)
        print("EYY ITS JUST SHOWING ALL PRODUCTS")
    
    categ  = Category.objects.all()
    context ={
        'products': products,
        'categ': categ,
        'main_cate': main_cat,
      
    }

    return render(request, 'user/products.html', context)
    

#This view shows the main category all products when we are in all products page
def p_view(request):
        main_cat      = MainCategory.objects.all()
    
        products      = Product.objects.all().filter(is_available=True)
        print("Entered P_VIEW")


        p             = Paginator(products,6)
        page      = request.GET.get('page')

        if page is not None:
            paged_product   = p.get_page(page)
        else:
            paged_product   = p.get_page(page)


        context = {
                'products' : products,
                # 'main_cat': main_cat,
                'products': paged_product,
        }

        return render(request, 'user/all_products.html', context)  


#This view shows the  one main category  products when filtered when we are in all products page
def main_p_view(request, id):
        print('THE ID IS NUMBER')
        main_cate            = MainCategory.objects.get(id=id)
        print(main_cate)
        categor      = Category.objects.filter(main_cate=main_cate)
        print(categor)
        productss   = Product.objects.filter(category__in=categor, is_available=True)
        print(productss)
        main_cat  = MainCategory.objects.all()
        print(main_cat)
        p             = Paginator(productss,6)
        page      = request.GET.get('page')

        if page is not None:
            paged_product   = p.get_page(page)
        else:
            paged_product   = p.get_page(page)

        context ={
            'main_cat': main_cat,
            'main_cate': main_cate.id,
            'products': paged_product,
            'categos': categor
            
        }

        return render(request, 'user/all_products.html', context)  






   

def p_details(request, category_slug, product_slug):
    main_cat      = MainCategory.objects.all()
    # products = Product.objects.all().filter(is_available=True)
    try:
        single_product   = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart          = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'main_cat': main_cat,
    }
    return render(request,'user/product_detail.html', context)

    

@login_required(login_url='signin')
def my_account(request):
        return render(request, 'user/myaccount.html', )



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



def order_return(request,id):
    user = request.user
    orders = Order.objects.get(id=id,user=user)
    orders.status = 'Returned'
    orders.save()
    return redirect('my_orders')





# def user_address(request):
#     address = UserProfile.objects.filter(user=request.user)
#     context={
#         'address': address
#     }
#     return render(request, 'user/user_address.html', context)




def user_address(request):
    address = Address.objects.filter(user=request.user)
    context={
        'address': address
    }
    return render(request, 'user/user_address.html', context)





# def add_address(request):
#     adrs  = UserProfile()
    
#     if request.method=="POST":
#         adrs.user               = request.user
#         adrs.address_line_1     = request.POST.get('address_line_1')
#         adrs.address_line_2     = request.POST.get('address_line_2')
#         adrs.city               = request.POST.get('city')
#         adrs.state              = request.POST.get('state')
#         adrs.country            = request.POST.get('country')
#         adrs.save()
#         messages.success(request, "Address Added")
#         return redirect(add_address)
#     context={
#         'adrs':adrs
#     }
#     return render(request, 'user/add_address.html', context)



def add_address(request):
    adrs     = Address()
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
        return redirect(add_address)
    context={
        'adrs':adrs
    }   
    return render(request, 'user/add_address.html', context)


def edit_address(request, id):
    adrs     = Address.objects.get(id=id)
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
        return redirect('edit_address', id)
    context={
        'adrs':adrs
    }   
    return render(request, 'user/edit_address.html', context)








# def buy_add_address(request):
#     adrs     = Address()
 
#     if request.method == "POST":
#         adrs.user               = request.user
#         adrs.name               = request.POST.get('name')
#         adrs.phone              = request.POST.get('phone')
#         adrs.email              = request.POST.get('email')
#         adrs.address_line       = request.POST.get('address_line_1')
#         adrs.pincode            = request.POST.get('pincode')
#         adrs.city               = request.POST.get('city')
#         adrs.state              = request.POST.get('state')
#         adrs.country            = request.POST.get('country')
#         adrs.save()
#         messages.success(request, "Address Added")
#         return redirect('buy_now')
#     context={
#         'adrs':adrs,
        
      
#     }   
#     return render(request, 'user/add_address.html', context)







def checkout_add_address(request):
    adrs     = Address()
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
        return redirect('checkout')
    context={
        'adrs':adrs
    }   
    return render(request, 'user/add_address.html', context)










def my_wallet(request):
    wl = Wallet.objects.all()
    users = request.user
    wall = 0
    count=0
    wallet = 0
    if Wallet.objects.filter(user = users).exists():
        wallet = Wallet.objects.get(user = users)
    else :
       wall = Wallet.objects.create(user = users)
       wall.save()
    return render(request, 'user/wallet.html', {'wallet': wall, 'wallet': wallet, 'wl':wl})






def add_ref(request):
    user = request.user
    cod = request.POST['code']
    print(cod)
    if user.referral_code != cod :
        print("Refer code")
        if Account.objects.filter(referral_code = cod).exists():
            usr = Account.objects.filter(referral_code = cod)
            print(usr)
            use = Wallet.objects.get(user = user)
            wall = use.balance + 375
            print(wall)
            
            userr = Wallet.objects.filter(user = user)
            userr.update(balance = wall)
            A  = Account.objects.filter(username = user)
            print(A)
            A.update(ref_active = True)
            messages.success(request,"Referel Successfull. Balance  Added to your Wallet, Happy Shopping !")
            return redirect('my_wallet') 
        else:
        
            print("Inner Else")
            messages.error(request,"You have entered wrong refferal code!")
            return redirect('my_account') 
    else:
        print("Outer else")
        messages.error(request,"You have entered wrong refferal code!")
        return redirect('my_account') 





def ref_cod_v(request):
    user = request.user.id
    usr =  Account.objects.get(id=user)
    print(usr)
    context = {
        'usr': usr
    }
    return render(request, 'user/refferal.html', context)





