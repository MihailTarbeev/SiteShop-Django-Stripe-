from django.contrib import admin
from .models import Item, Category
from django.utils.safestring import mark_safe


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('name', "item_image", "image", "slug", 'price', 'owner',
              'is_available', 'category')
    list_display = ("name", "item_image", 'owner',
                    "is_available", "category", "created_at", "updated_at")
    readonly_fields = ["item_image",]
    list_editable = ("is_available",)
    ordering = ('created_at',)

    @admin.display(description='Миниатюрное изображение')
    def item_image(self, item: Item):
        if item.image:
            return mark_safe(f"<img src='{item.image.url}' width=50>")
        return "Без фото"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    ordering = ('id',)
