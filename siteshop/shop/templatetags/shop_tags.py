import random
from django import template
from shop.models import Category
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('shop/categories.html')
def show_categories(category_selected=0):
    categories = Category.objects.filter(items__is_available=True).annotate(
        total=Count("items")).filter(total__gt=0).order_by("name")
    return {'categories': categories, 'category_selected': category_selected}


@register.simple_tag
def shuffled_items(items):
    tmp = list(items)[:]
    random.shuffle(tmp)
    return tmp
