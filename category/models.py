
from django.db import models
from django.urls import reverse

# Create your models here.

class MainCategory(models.Model):
    
    name                    = models.CharField(max_length=20)

    
    class Meta:
        verbose_name        = 'main category'
        verbose_name_plural = 'Main Category'

    def __str__(self):
        return self.name





class Category(models.Model):
    main_cate   = models.ForeignKey(MainCategory,related_name='subcategory', on_delete=models.CASCADE, null=True)
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)


    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])



    def __str__(self):
        return self.category_name
    

