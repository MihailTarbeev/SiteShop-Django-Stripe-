from django.contrib import admin
from .models import Item, Category, Tax, Discount
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.core.exceptions import ValidationError


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('name', "item_image", "image", "slug", 'price', "currency", 'owner',
              'is_available', 'category', "taxes")
    list_display = ("name", "item_image", 'owner',
                    "is_available", "category", "created_at", "currency",)
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


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    fields = ("display_name", "percentage", "stripe_tax_id", "active",
              "description")

    list_display = ("display_name", "percentage", "stripe_tax_id", "inclusive", "active",
                    "description", "created_at", "updated_at")
    ordering = ('created_at',)
    actions = ['delete_selected']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["stripe_tax_id", "percentage",
                    "created_at", "updated_at", "inclusive"]
        else:
            return ["stripe_tax_id",
                    "created_at", "updated_at", "inclusive"]

        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
            messages.success(
                request, f'Налог "{obj.display_name}" успешно сохранен ЭЭЭ')

        except ValidationError as e:
            messages.add_message(request, messages.ERROR, str(e))
        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e))

    def delete_model(self, request, obj):
        try:
            obj.delete()
            messages.success(request, f'Налог "{obj.display_name}" удален')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')

    def delete_selected(self, request, queryset):
        count_taxs = 0
        errors = []

        for obj in queryset:
            try:
                obj.delete()
                count_taxs += 1
            except Exception as e:
                errors.append(f"{obj.display_name}: {str(e)}")

        if count_taxs:
            message = f'Успешно удалено {count_taxs} налогов'
        if errors:
            message += f'/nОшибки: {", ".join(errors)}'

            self.message_user(request, message)

        return None

    delete_selected.short_description = "Удалить выбранные налоги"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    fields = ("name", "stripe_coupon_id", "percent_off", "amount_off", "currency", "duration",
              "duration_in_months", "is_active", "created_at", "updated_at")

    list_display = ("name", "stripe_coupon_id", "percent_off", "currency",
                    "duration", "duration_in_months", "is_active", "created_at", "updated_at")
    ordering = ('created_at',)
    actions = ['delete_selected']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("stripe_coupon_id", "percent_off", "amount_off", "currency",
                    "duration", "duration_in_months", "is_active", "created_at", "updated_at")
        else:
            return ("stripe_coupon_id", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
            messages.success(request, f'Купон "{obj.name}" сохранён.')
        except Exception as e:
            messages.error(request, str(e))

    def delete_model(self, request, obj):
        try:
            obj.delete()
            messages.success(request, f'Купон "{obj.name}" удален.')
        except Exception as e:
            messages.error(request, str(e))

    def delete_selected(self, request, queryset):
        count_taxs = 0
        errors = []

        for obj in queryset:
            try:
                obj.delete()
                count_taxs += 1
            except Exception as e:
                errors.append(f"{obj.display_name}: {str(e)}")

        if count_taxs:
            message = f'Успешно удалено {count_taxs} купонов'
        if errors:
            message += f'/nОшибки: {", ".join(errors)}'
            self.message_user(request, message)
        return None

    delete_selected.short_description = "Удалить выбранные купоны"
