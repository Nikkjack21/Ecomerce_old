import datetime
import os
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login, logout
from accounts.models import Account
from category.models import Category, MainCategory
from store.models import Product
from slugify import slugify
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from orders.models import Order, OrderProduct, Payment, RazorPay
from cartapp.models import CategoryOffer, Coupon, ProductOffer
from .forms import CouponAdminForm, OrderEditForm, ProductOfferForm, CategoryOfferForm
from django.db.models import Sum,Count
from django.db.models.functions import TruncDate, TruncDay, TruncMonth, TruncWeek
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import ExtractMonth,ExtractDay
import calendar
# Create your views here.


@cache_control (must_revalidate=True, no_cache=True, no_store=True)
def admin_signin(request):
    if request.user.is_authenticated and request.user.is_admin:
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
    #ORDER GRAPH
    orderbyday = Order.objects.annotate(day=ExtractDay('created_at')).values('day').annotate(count=Count('id'))
    print(orderbyday)
    dayday =[]
    orderperday =[]
    for o in orderbyday:
        dayday.append(o['day'])
        orderperday.append(o['count'])
    order = Order.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).values('month','count')
    monthNumber = []
    totalOrder = []
    for ord in order:
        monthNumber.append(calendar.month_name[ord['month']])
        totalOrder.append(ord['count'])
    #total users
    users_count = Account.objects.all().count()

    #total revenue
    revenue=0
    order = OrderProduct.objects.all()
    for item in order:
        revenue = revenue + item.product_price

    #total order
    order_count = Order.objects.all().count()

 
    completed_order = Order.objects.filter(status='Completed').count()
    pending_order = Order.objects.filter(status='Order Confirmed').count()
    accepted_order = Order.objects.filter(status='Accepted').count()
    cancelled_order = Order.objects.filter(status='Cancelled').count()
    Returned_order = Order.objects.filter(status='Returned').count()
    order_status_list = []
    order_status_list.append(completed_order)
    order_status_list.append(accepted_order)
    order_status_list.append(pending_order)
    order_status_list.append(cancelled_order)
    order_status_list.append(Returned_order)
    print(order_status_list)
    recent_order = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'monthNumber':monthNumber,
        'totalOrder':totalOrder,
        'dayday':dayday,
        'orderperday':orderperday,
        'users_count':users_count,
        'revenue':revenue,
        'order_count':order_count,
        'order_status_list':order_status_list,
        'recent_order': recent_order
     
        }
    return render(request, 'adm/admin_index.html', context)

def admin_out(request):
    logout(request)
    return redirect(admin_signin)

#USER MANAGEMENT DETAILS BEGINS HERE------------>

def users_details(request):
    users     = Account.objects.all().order_by('id')
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


def main_view(request):
    main_cat  = MainCategory.objects.all()
    return render(request, 'adm/main_cat.html', {"main_cat": main_cat})



def main_add(request):
    main     = MainCategory()
    if request.method == "POST":
        main.name       = request.POST.get('name')

        var1  = main.name

        if MainCategory.objects.filter(name=main.name).exists():
            messages.info(request, "Main Category {} already exists " .format(var1))
            print('Main category exits')
            return redirect(main_add)
            

        if main.name =='' :
            messages.info(request, "Category fields cannot be blank")
            print('Filed blank')
            return redirect(main_add)
        main.save()
        print("CATEGORY ADDEDD SUCCESSFULLY")
        messages.info(request, "Category Added")
        return redirect(main_view)
    return render(request, 'adm/main_add.html')
        
        


# def main_edit(request, id):
#     obj =MainCategory.objects.get(id=id)
#     if request.method == 'POST':
#         obj.name              = request.POST.get('name')
#         obj.save()
#         return redirect(main_view)
#     context = {
#         'obj': obj
#     }
#     return render(request, 'adm/main_edit.html', context)



def main_del(request, id):
    delCat = MainCategory.objects.get(id=id)
    delCat.delete()
    return redirect(main_view)

#MAIN CATEGORY MANAGEMENT DETAILS ENDS HERE------------>





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
      

        new.category_name       = request.POST.get('category_name')
        new.description         = request.POST.get('description')
        new.slug                = slugify(new.category_name)

        var1  = new.category_name

        if Category.objects.filter(category_name=new.category_name).exists():
            messages.info(request, "Category {} already exists " .format(var1))
            print('category exits')
            return redirect('AddCategory')


        if new.category_name =='' :
            messages.info(request, "Category fields cannot be blank")
            print('Filed blank')
            return redirect('AddCategory')
            
        if len(request.FILES) != 0:
            print('ENTERING IMAGE')
            new.cat_image       = request.FILES.get('image')   
            print("IMAGE ADDED")
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
            pro_obj.images              = request.FILES.get('image')    
            pro_obj.images_two          = request.FILES.get('image2')    
            pro_obj.images_three        = request.FILES.get('image3')    
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

            if product_detail.images_two:
                os.remove(product_detail.images.path)
            product_detail.images_two       = request.FILES.get('image2')

            if product_detail.images_three:
                os.remove(product_detail.images.path)
            product_detail.images_three       = request.FILES.get('image3')

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



def order_list(request):
    orders = Order.objects.all().order_by('-id')
    # payments = Payment.objects.all()
    return render(request, 'adm/order_list.html', {'orders': orders})


def order_actions(request, id):
    order  = Order.objects.filter(id=id)
    order.update(status='Cancelled')
    return redirect('order_list')




def change_status(request,id):
    orders = Order.objects.get(id=id)
    print(orders)
    form = OrderEditForm(instance=orders)
    if request.method=='POST':
        form = OrderEditForm(request.POST)
        status = request.POST.get('status')
        orders.status = status
        orders.save()
        return redirect ('order_list')
    context = {
        'orders':orders,
        'form':form
    }
    return render(request,'adm/change_status.html',context)







def offer_product(request):
    off_pro  = ProductOffer.objects.all()

    context = {
        'off_pro': off_pro,
    }
    return render(request, 'adm/product_offer.html', context)


def add_offer_pro(request):
    form = ProductOfferForm(request.POST)
    print("hello pro offer    OFFER IS ACTUALL WORKING")
    if form.is_valid():
        form.save()
        messages.info(request,'Product offer added successfully')
        return redirect(offer_product)
    context ={
        'form':form
    }
    return render(request, 'adm/add_product_offer.html', context)


def edit_pro_offer(request,id):
    offer = ProductOffer.objects.get(id=id)
    form = ProductOfferForm(instance=offer)
    if request.method =="POST":
        form = ProductOfferForm(request.POST,instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request,'Product offer updated successfully')
            return redirect('product_offer')
    return render (request,'adm/edit_product_offer.html',{'form':form,'offer':offer})


def delete_pro_offer(request, id):
    offer = ProductOffer.objects.get(id=id)
    offer.delete()
    return redirect(offer_product)


def offer_category(request):
    off_cat  = CategoryOffer.objects.all()

    context = {
        'off_cat': off_cat,
    }
    return render(request, 'adm/category_offer.html', context)


def add_offer_cat(request):
    form = CategoryOfferForm(request.POST)
    print("hello category offer    OFFER IS ACTUALL WORKING")
    if form.is_valid():
        form.save()
        messages.info(request,'Category offer added successfully')
        return redirect(offer_category)
    context ={
        'form':form
    }
    return render(request, 'adm/add_cat_offer.html', context)

def edit_cat_offer(request,id):
    offer = CategoryOffer.objects.get(id=id)
    form = CategoryOfferForm(instance=offer)
    if request.method =="POST":
        form = CategoryOfferForm(request.POST,instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request,'Category offer updated successfully')
            return redirect(offer_category)
    return render (request,'adm/edit_cat_offer.html',{'form':form,'offer':offer})



def delete_cat_offer(request, id):
    offer = CategoryOffer.objects.get(id=id)
    offer.delete()
    return redirect('cat_offer')







def sales_report(request):
    salesreport = Order.objects.all().order_by('-created_at')
    total = 0
    total= salesreport.aggregate(Sum('order_total')).get('order_total__sum')
    RoundTotal =("{:0.2f}".format(total))

    
    p           = Paginator(salesreport, 10)
    page_num  = request.GET.get('page')
    try:
        page        = p.page (page_num)
    # except EmptyPage:
    #     page        = p.page(1)
    except PageNotAnInteger:
        page        = p.page(1)

    
    context = {
        
        # 'salesreport': salesreport,
        'RoundTotal': RoundTotal,
        'items':page,

    }
    return render(request,'adm/sales_report.html',context)




def monthly_report(request,date):
    context = None
    frmdate = date
   
    fm = [ 2022 , frmdate , 1 ]
    todt = [2022 , frmdate , 28 ]
    
    print(fm)
            
    salesreport = Order.objects.filter(created_at__gte=datetime.date(fm[0],fm[1],fm[2]), created_at__lte=datetime.date(todt[0],todt[1],todt[2])).annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).annotate(sum=Sum('order_total')).order_by('-day')
    
    if len(salesreport) > 0 :   
        context = {
                'salesreport' : salesreport ,  
               
            }
        print(salesreport)
        print("Showing monthly Orders")
        return render(request,'adm/search_report_sales.html',context)
    else:
        print("Showing No monthly Orders")
        messages.error(request, "No orders in this month")
    return render(request,'adm/sales_report.html',context)






def yearly_report(request,date):
    context = None
    frmdate = date
   
    fm = [ frmdate , 1 , 1 ]
    todt = [frmdate , 12 , 30 ]
    
    print(fm)
            
    salesreport = Order.objects.filter(created_at__gte=datetime.date(fm[0],fm[1],fm[2]), created_at__lte=datetime.date(todt[0],todt[1],todt[2])).annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).annotate(sum=Sum('order_total')).order_by('-day')
    if len(salesreport) > 0 :   
        context = {
                'salesreport' : salesreport ,   
            }
        print(salesreport)
        print("Showing yearly Orders")
        return render(request,'adm/search_report_sales.html',context)
    else:
        print("No Orders")
        messages.info(request,"No Orders")
    return render(request,'adm/sales_report.html',context)



# def weekly_report(request,date):
#     context = None
#     frmdate = date
   
#     fm = [ 2022 , 1 , frmdate ]
#     todt = [2022 , 12 , frmdate ]
    
#     print(fm)
            
#     salesreport = Order.objects.filter(created_at__gte=datetime.date(fm[0],fm[1],fm[2]), created_at__lte=datetime.date(todt[0],todt[1],todt[2])).annotate(day=TruncWeek ('created_at')).values('weekly').annotate(count=Count('id')).annotate(sum=Sum('order_total')).order_by('-weekly')
#     if len(salesreport) > 0 :   
#         context = {
#                 'salesreport' : salesreport ,   
#             }
#         print(salesreport)
#         print("222222222222222222222222222222222222222")
#         return render(request,'adm/search_report_sales.html',context)
#     else:
#         print("44444444444444444")
#         messages.info(request,"No Orders")
#     return render(request,'adm/sales_report.html',context)





def show_result(request):
    order = Order.objects.all()

    pag   = sales_report(request)
    print(pag)
    print('Pagination')
    if request.method == "POST":
        fromdate =request.POST.get('fromdate')
        todate =request.POST.get('todate')
        if len(fromdate)<=0 or len(fromdate) <=0:
            print('fromdate is Zero')
            messages.error(request, "Please enter date correctly")
            return redirect(sales_report)
    

        if len(fromdate) > 0 or len(todate) > 0 :
            frm = fromdate.split("-")
            tod = todate.split("-")

            fm = [int(x) for x in frm]
            todt = [int(x) for x in tod]
            print(fm)

                
            salesreport = Order.objects.filter(created_at__gte=datetime.date(fm[0],fm[1],fm[2]), created_at__lte=datetime.date(todt[0],todt[1],todt[2])).annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).annotate(sum=Sum('order_total')).order_by('-day')
            
            context = {

                'salesreport' : salesreport ,   
                'pag':pag,

            }
            print(salesreport)
            print("111")
            return render(request,'adm/search_report_sales.html',context)
        else:
            report_sales = Order.objects.all()
            context = {
                'salesreport': report_sales ,
                'pag':pag,

             }
            return render(request,'adm/sales_report.html',context)

    else:
        salesreport_all = Order.objects.all()
        context = {
            'salesreport': salesreport_all ,
            'pag':pag
          
        

        }
        return render(request,'adm/search_report_sales.html',context)





def coupon_list(request):
    coupon   = Coupon.objects.all()
    return render(request, 'adm/coupon_list.html', {'coupon': coupon})




def add_coupon(request):
    form = CouponAdminForm(request.POST)
    if form.is_valid():
        form.save()
        messages.info(request,'coupon added successfully')
        return redirect('coupon_list')
    context ={
        'form':form
    }
    return render (request,'adm/add_coupon.html',context)


def edit_coupon(request,id):
    coupon = Coupon.objects.get(id=id)
    form = CouponAdminForm(instance=coupon)
    if request.method =="POST":
        form = CouponAdminForm(request.POST,instance=coupon)
        form.save()
        messages.success(request,'coupon updated successfully')
        return redirect('coupon_list')
    return render (request,'adm/edit_coupon.html',{'form':form,'coupon':coupon})


def delete_coupon(request,id):
    coupon = Coupon.objects.get(id=id)
    coupon.delete()
    return redirect('coupon_list')