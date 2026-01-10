from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.validators import RussianValidator
import stripe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from .utils import CURRENCY_CHOICES, MIN_AMOUNTS


class Tax(models.Model):
    """Модель налогов"""
    display_name = models.CharField(max_length=50, verbose_name="Название")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Процентная ставка", validators=(
        MinValueValidator(0), MaxValueValidator(100)))
    stripe_tax_id = models.CharField(
        max_length=100, blank=True, verbose_name="ID в Stripe", editable=False)
    inclusive = models.BooleanField(
        default=False, verbose_name="Включение в цену")
    active = models.BooleanField(default=True, verbose_name="Активен")
    country = models.CharField(max_length=2, null=True, blank=True,
                               verbose_name="Код страны", help_text="ISO 3166-1")
    description = models.TextField(
        max_length=150, null=True, blank=True, verbose_name="Описание")
    jurisdiction = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Юрисдикция")
    state = models.CharField(max_length=50, null=True,
                             blank=True, verbose_name="Регион (Штат)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} ({self.percentage}%)"

    def save(self, *args, **kwargs):
        try:
            if not self.stripe_tax_id:
                tax_rate = stripe.TaxRate.create(
                    display_name=self.display_name,
                    percentage=float(self.percentage),
                    inclusive=self.inclusive,
                    active=self.active,
                    country=self.country if self.country else None,
                    description=self.description if self.description else None,
                    jurisdiction=self.jurisdiction if self.jurisdiction else None,
                    state=self.state if self.state else None,
                )

                self.stripe_tax_id = tax_rate.id

            else:
                stripe.TaxRate.modify(
                    self.stripe_tax_id,
                    display_name=self.display_name,
                    active=self.active,
                    description=self.description,
                    country=self.country,
                    jurisdiction=self.jurisdiction,
                    state=self.state,
                )

            super().save(*args, **kwargs)

        except Exception as e:
            raise ValidationError(f"Ошибка при сохранении налога: {str(e)}")

    def delete(self, *args, **kwargs):
        """Удаляет налоговую ставку из Stripe при удалении из БД"""
        try:
            if self.stripe_tax_id:
                stripe.TaxRate.modify(
                    self.stripe_tax_id,
                    active=False
                )
                self.active = False
                self.save()
            super().delete(*args, **kwargs)

        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка при деактивации налога: {str(e)}")

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_available=True)


class Item(models.Model):
    """Модель товара"""
    name = models.CharField(
        max_length=200, verbose_name="Название товара", validators=[RussianValidator(),])

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[
                                MinValueValidator(0)], verbose_name="Цена")

    description = models.TextField(blank=True, verbose_name="Описание")

    owner = models.ForeignKey(get_user_model(),
                              on_delete=models.CASCADE, related_name='items', verbose_name="Владелец")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления")

    is_available = models.BooleanField(
        default=True, verbose_name="Доступен для продажи")

    image = models.ImageField(
        upload_to='items/%Y/%m/%d/', blank=True, verbose_name="Изображение")

    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, related_name="items", verbose_name="Категория")

    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL",)

    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0][0], verbose_name="Валюта",)

    taxes = models.ManyToManyField(
        Tax,
        blank=True,
        related_name='items',
        verbose_name="Налоги",
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-name"]

    def get_absolute_url(self):
        return reverse("item", kwargs={"item_slug": self.slug})

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории товаров"""
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="Название категории")

    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})


class Discount(models.Model):
    """Модель купонов"""

    DURATION_CHOICES = [
        ('forever', 'Навсегда'),
        ('once', 'Один раз'),
        ('repeating', 'Повторяющийся'),
    ]

    name = models.CharField(max_length=40, verbose_name="Название купона", )

    stripe_coupon_id = models.CharField(
        max_length=100, blank=True, verbose_name="ID купона в Stripe", editable=False)

    amount_off = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма скидки",)

    percent_off = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      verbose_name="Процент скидки", validators=[MinValueValidator(0), MaxValueValidator(100)])

    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True, verbose_name="Валюта",)

    duration = models.CharField(max_length=10, choices=DURATION_CHOICES,
                                default='forever', verbose_name="Длительность действия")

    duration_in_months = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Количество месяцев",)

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.amount_off:
            return f"{self.name} - {self.amount_off} {self.currency}"
        return f"{self.name} - {self.percent_off}%"

    def clean(self):
        errors = {}

        if self.amount_off and self.percent_off:
            errors['amount_off'] = 'Укажите либо сумму, либо процент скидки, но не оба.'

        if self.amount_off and not self.currency:
            errors['currency'] = 'Валюта обязательна для скидки с фиксированной суммой.'

        if self.duration == 'repeating' and not self.duration_in_months:
            errors['duration_in_months'] = 'Для повторяющихся купонов укажите количество месяцев.'

        if self.duration != 'repeating' and self.duration_in_months:
            errors['duration_in_months'] = 'Количество месяцев указывается только для повторяющихся купонов.'

        if self.amount_off and self.amount_off <= 0:
            errors['amount_off'] = 'Сумма скидки должна быть положительной.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        try:
            if not self.stripe_coupon_id:
                coupon_params = {
                    'name': self.name,
                    'duration': self.duration,
                }

                if self.amount_off:
                    coupon_params['amount_off'] = int(self.amount_off * 100)
                    coupon_params['currency'] = self.currency.lower()
                else:
                    coupon_params['percent_off'] = float(self.percent_off)

                if self.duration == 'repeating' and self.duration_in_months:
                    coupon_params['duration_in_months'] = self.duration_in_months

                coupon = stripe.Coupon.create(**coupon_params)
                self.stripe_coupon_id = coupon.id
            else:
                stripe.Coupon.modify(
                    self.stripe_coupon_id,
                    name=self.name
                )
            super().save(*args, **kwargs)

        except Exception as e:
            raise ValidationError(f'Ошибка при сохранении: {str(e)}')

    def delete(self, *args, **kwargs):
        try:
            if self.stripe_coupon_id:
                stripe.Coupon.delete(self.stripe_coupon_id)
        except Exception as e:
            raise ValidationError(f'Ошибка при удалении: {e}')

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Купон"
        verbose_name_plural = "Купоны"
        ordering = ['-created_at']


class Cart(models.Model):
    """Модель корзины"""
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user.username}"

    def get_total_price(self):
        total = 0
        for cart_item in self.items.all():
            total += cart_item.calculate_total_price()
        return total

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def is_empty(self):
        return self.items.count() == 0


class CartItem(models.Model):
    """Модель для связи моделей Items и Cart"""
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'item']
        verbose_name = "Товары в корзине"
        verbose_name_plural = "Товары в корзине"

    def __str__(self):
        return f"{self.cart.user.username} {self.item.name}"

    def calculate_total_price(self):
        return self.item.price * self.quantity
