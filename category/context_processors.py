from .models import MainCategory
from store.models import Product

def menu_links(request):
    main_cat      = MainCategory.objects.all()
    products = Product.objects.all().filter(is_available=True)

    return{'main_cat': main_cat, 'products': products}
