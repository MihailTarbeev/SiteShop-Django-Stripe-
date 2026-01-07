from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.validators import RussianValidator


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
