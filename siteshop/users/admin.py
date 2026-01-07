from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.safestring import mark_safe


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name',
         'last_name', 'photo', 'user_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ('username', "user_photo", 'email', 'first_name',
                    'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_display_links = ('username', 'email')
    ordering = ('-date_joined', 'email')
    readonly_fields = ('date_joined', 'last_login', 'username', "user_photo")

    @admin.display(description='Изображение', ordering="content")
    def user_photo(self, user: User):
        if user.photo:
            return mark_safe(f"<img src='{user.photo.url}' width=50>")
        return "Без фото"
