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

    # def get_current_rank(self):
    #     from shop.models import RankCategory

    #     total = self.get_total_spent()
    #     rank = RankCategory.objects.filter(
    #         min_total__lte=total
    #     ).order_by('-min_total').first()

    #     return rank

    # def get_next_rank(self):
    #     from shop.models import RankCategory

    #     total = self.get_total_spent()
    #     next_rank = RankCategory.objects.filter(
    #         min_total__gt=total
    #     ).order_by('min_total').first()

    #     return next_rank

    # def get_rank_progress(self):
    #     """Возвращает данные о прогрессе до следующего ранга"""
    #     total_spent = self.get_total_spent()
    #     current_rank = self.get_current_rank()
    #     next_rank = self.get_next_rank()

    #     if not current_rank:
    #         return None

    #     if not next_rank:
    #         return {
    #             'current_rank': current_rank,
    #             'next_rank': None,
    #             'total_spent': total_spent,
    #             'progress_percent': 100,
    #             'needed': 0,
    #             'is_max_rank': True
    #         }

    #     current_min = float(current_rank.min_total)
    #     next_min = float(next_rank.min_total)
    #     spent_from_current = total_spent - current_min
    #     needed_for_next = next_min - current_min

    #     progress_percent = (spent_from_current / needed_for_next) * \
    #         100 if needed_for_next > 0 else 0

    #     return {
    #         'current_rank': current_rank,
    #         'next_rank': next_rank,
    #         'total_spent': total_spent,
    #         'progress_percent': min(100, max(0, progress_percent)),
    #         'needed': max(0, next_min - total_spent),
    #         'is_max_rank': False
    #     }

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
