from .models import MainCategory

def menu_links(request):
    links = MainCategory.objects.all
    return dict(links=links)    