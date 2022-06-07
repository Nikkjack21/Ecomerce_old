from email.mime import image
from multiprocessing import context
import os
from threading import local
from unicodedata import category, name
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login, logout
from accounts.models import Account
from category.models import Category
from store.models import Product
from slugify import slugify
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# Create your views here.


@cache_control (must_revalidate=True, no_cache=True, no_store=True)
def admin_signin(request):
    if request.user.is_authenticated:
        return redirect(admin_home)
    if request.method == 'POST':
        username        = request.POST.get('username')
        password        = request.POST.get('password')
        user            = authenticate(username=username, password=password)


        if username == '' and password == '':
            messages.error(request,"Please enter credentials")
            return redirect(admin_signin)
        if user is not None:
            if user.is_admin==True:
                login(request,user)
                print('GOING HOME')
                return redirect(admin_home)
            else:
                messages.error(request, 'You are not authorized')
                print('SORRY CANT GOING HOME')  
                return redirect(admin_signin)
        else:
            messages.error(request,'INVALID CREDENTIALS' )   
            return redirect(admin_signin)

    return render(request, 'adm/admin_login.html')

@cache_control (must_revalidate=True, no_cache=True, no_store=True)
@login_required(login_url='adminsignin/')
def admin_home(request):
    return render(request, 'adm/admin_index.html')

def admin_out(request):
    logout(request)
    return redirect(admin_signin)

#USER MANAGEMENT DETAILS BEGINS HERE------------>

def users_details(request):
    users     = Account.objects.all()
    context   =  {
        'users': users
    }
    return render(request, 'adm/users_admin.html', context)

def action_user(request, id):
    user_action     = Account.objects.get(id=id)
    if user_action.is_active:
        user_action.is_active = False
        user_action.save()
       
    else:
        user_action.is_active = True
        user_action.save()
    return redirect(users_details)


#USER MANAGEMENT DETAILS ENDS HERE------------>

#CATEGORY MANAGEMENT DETAILS BEGINS HERE------------>

def cate_view(request):
    cate = Category.objects.all()
    context={
        'cate': cate
    }
    return render(request, 'adm/category_list.html', context)


def cate_add(request):
    new = Category()
    if request.method == 'POST':
      
        if len(new.category_name) == 0 :
            messages.info(request, "Category fields cannot be blank")
            return redirect('AddCategory')
        new.category_name       = request.POST.get('category_name')
        new.description         = request.POST.get('description')
        new.slug                = slugify(new.category_name)

        if len(request.FILES) != 0:
            new.cat_image       = request.FILES.get('image')   
        new.save()
        print("CATEGORY ADDEDD SUCCESSFULLY")
        return redirect(cate_view)
    return render(request, 'adm/category_add.html')




def cate_edit(request, id):
    obj = Category.objects.get(id=id)
    
    if request.method == 'POST':
        if len(request.FILES) != 0:
            try:
                if len(obj.cat_image)>0:
                    os.remove(obj.cat_image.path)
            except:     
                    obj.cat_image      = request.FILES.get('image')   
        obj.category_name              = request.POST.get('category_name')
        obj.description                = request.POST.get('description')
        obj.slug                       = slugify(obj.category_name)
        obj.save()
        return redirect(cate_view)

    context = {
        'obj': obj
    }
    return render(request, 'adm/category_edit.html', context)


def cate_del(request, id):
    delCat = Category.objects.get(id=id)
    delCat.delete()
    return redirect(cate_view)


#CATEGORY MANAGEMENT DETAILS ENDS HERE------------>


#PRODUCT MANAGEMENT DETAILS BEGINS HERE------------>


def product_view(request):
    pro = Product.objects.all()
    context={
        'pro':pro
    }
    return render(request, 'adm/product_view.html', context)

def prouct_add(request):
    pro_obj = Product()
    if request.method == "POST":

        pro_obj.product_name        = request.POST.get('product_name')
        pro_obj.description         = request.POST.get('description')
        pro_obj.price               = request.POST.get('price')
        pro_obj.stock               = request.POST.get('stock')
        categ                       = request.POST.get('category')
        pro_obj.slug                = slugify(pro_obj.product_name)

        if len(pro_obj.product_name) == 0 or len(categ) == 0:
            messages.error(request, 'Fields cannot be blank')
            return redirect(prouct_add)

        pro_obj.category            = Category.objects.get(id=categ)

        if len(request.FILES) != 0:
            pro_obj.images          = request.FILES.get('image')    
            pro_obj.save()
        else:
            messages.error(request, "Please insert an image ")
            print('please insert an image')
            return redirect(prouct_add)
        return redirect(product_view)
             
    
    cate = Category.objects.all()
    return render(request, 'adm/product_add.html', {'cate': cate}, )
    

def product_edit(request, id):
    product_detail = Product.objects.get(id=id)
    if request.method == 'POST':
        if len(request.FILES) != 0:
            if product_detail.images:
                os.remove(product_detail.images.path)
            product_detail.images       = request.FILES.get('image')
        product_detail.product_name     = request.POST.get('product_name')
        product_detail.description      = request.POST.get('description')
        product_detail.price            = request.POST.get('price')
        product_detail.stock            = request.POST.get('stock')


        product_detail.save()   
        print('UPDATED SUCCESS!!!!')
        return redirect(product_view)

    product     = Product.objects.get(id=id)
    cate        = Category.objects.all()
    return render(request, 'adm/product_edit.html', {'product': product, 'cate': cate} )

def product_delete(request, id):
    product_del  = Product.objects.get(id=id)
    product_del.delete()
    return redirect(product_view)


#PRODUCT MANAGEMENT DETAILS ENDS HERE------------>