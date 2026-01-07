from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', "photo", 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined'
    )
    list_display_links = ('username', 'email')
    ordering = ('-date_joined', 'email')
    readonly_fields = ('date_joined', 'last_login', 'username')
