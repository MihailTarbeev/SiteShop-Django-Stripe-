from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.validators import RussianValidator
import stripe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_available=True)


class Item(models.Model):
    """Модель товара"""
    name = models.CharField(
        max_length=200,
        verbose_name="Название товара", validators=[RussianValidator(),]
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Владелец"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступен для продажи"
    )

    image = models.ImageField(
        upload_to='items/%Y/%m/%d/', blank=True, verbose_name="Изображение")

    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name="items", verbose_name="Категория")

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL",
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
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название категории"
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})


class Tax(models.Model):
    """Модель налогов"""
    display_name = models.CharField(max_length=50, verbose_name="Название")
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Процентная ставка", validators=(MinValueValidator(0), MaxValueValidator(100))
    )
    stripe_tax_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID в Stripe",
        editable=False
    )
    inclusive = models.BooleanField(
        default=False,
        verbose_name="Включение в цену"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    country = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        verbose_name="Код страны",
        help_text="ISO 3166-1"
    )
    description = models.TextField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Описание"
    )
    jurisdiction = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Юрисдикция"
    )
    state = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Регион (Штат)"
    )

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
                stripe.TaxRate.modify(  # можно изменять только active, country, description, display_name, jurisdiction, state
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
