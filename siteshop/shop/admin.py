from django.contrib import admin
from .models import Item, Category


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', "slug", 'price', 'owner',
                    'is_available', 'created_at', 'category')
    ordering = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    ordering = ('id',)
