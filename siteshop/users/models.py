from datetime import timedelta
import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import bcrypt
from django.utils import timezone
from django.contrib.auth.hashers import check_password as django_check_password
from .validators import RussianValidator
# from shop.models import Order, Discount


class User(AbstractUser):
    photo = models.ImageField(
        upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name="Фото")
    first_name = models.CharField(
        max_length=150, validators=[RussianValidator(),], verbose_name="Имя")
    last_name = models.CharField(
        max_length=150, validators=[RussianValidator(),], verbose_name="Фамилия")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def get_total_spent(self):
        """Сумма всех оплаченных заказов в рублях"""
        from shop.models import Order, Currency

        total_in_rubles = 0
        paid_orders = Order.objects.filter(user=self, status='Paid')

        for order in paid_orders:
            total_in_rubles += Currency.convert_amount_to_rubles(
                order.total_amount,
                order.currency.code
            )

        return round(total_in_rubles, 2)
