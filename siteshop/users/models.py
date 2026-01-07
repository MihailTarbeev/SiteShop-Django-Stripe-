from datetime import timedelta
import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import bcrypt
from django.utils import timezone
from django.contrib.auth.hashers import check_password as django_check_password
from django.contrib.auth.models import BaseUserManager
from .validators import RussianValidator


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

# class Role(models.Model):
#     """Таблица ролей"""
#     name = models.CharField(max_length=50, unique=True,
#                             verbose_name="Название роли")
#     description = models.TextField(blank=True, verbose_name="Описание")

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Роль"
#         verbose_name_plural = "Роли"


# class BusinessElement(models.Model):
#     """Таблица бизнес-объектов"""
#     name = models.CharField(max_length=100, unique=True,
#                             verbose_name="Название объекта")
#     description = models.TextField(blank=True, verbose_name="Описание")

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Бизнес-объект"
#         verbose_name_plural = "Бизнес-объекты"


# class AccessRoleRule(models.Model):
#     """Таблица правил доступа ролей к объектам"""
#     role = models.ForeignKey(Role, on_delete=models.CASCADE,
#                              related_name='access_rules', verbose_name="Роль")
#     element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE,
#                                 related_name='access_rules', verbose_name="Бизнес-объект")

#     read_permission = models.BooleanField(
#         default=False, verbose_name="Чтение своих")
#     read_all_permission = models.BooleanField(
#         default=False, verbose_name="Чтение всех")
#     create_permission = models.BooleanField(
#         default=False, verbose_name="Создание")
#     update_permission = models.BooleanField(
#         default=False, verbose_name="Обновление своих")
#     update_all_permission = models.BooleanField(
#         default=False, verbose_name="Обновление всех")
#     delete_permission = models.BooleanField(
#         default=False, verbose_name="Удаление своих")
#     delete_all_permission = models.BooleanField(
#         default=False, verbose_name="Удаление всех")

#     class Meta:
#         verbose_name = "Правило-доступа"
#         verbose_name_plural = "Правила-доступа"


# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Email обязателен')
#         if 'first_name' not in extra_fields:
#             raise ValueError('Имя обязательно')
#         if 'last_name' not in extra_fields:
#             raise ValueError('Фамилия обязательна')

#         email = self.normalize_email(email)

#         if 'role' not in extra_fields:
#             user_role, created = Role.objects.get_or_create(
#                 name='User',
#                 defaults={'description': 'Обычный пользователь'}
#             )
#             extra_fields['role'] = user_role

#         user = self.model(email=email, **extra_fields)

#         if password:
#             user.set_password(password)
#         else:
#             user.set_unusable_password()

#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         admin_role, created = Role.objects.get_or_create(
#             name='Admin',
#             defaults={'description': 'Полный доступ ко всему'}
#         )

#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('role', admin_role)

#         return self.create_user(email, password, **extra_fields)


# class Session(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     session_key = models.CharField(max_length=255, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     is_active = models.BooleanField(default=True)

#     @classmethod
#     def create_session(cls, user):
#         session_key = secrets.token_urlsafe(64)
#         expires_at = timezone.now() + timedelta(days=7)

#         cls.objects.create(
#             user=user,
#             session_key=session_key,
#             expires_at=expires_at
#         )
#         return session_key

#     def is_valid(self):
#         return self.is_active and timezone.now() < self.expires_at

#     class Meta:
#         verbose_name = "Сессия"
#         verbose_name_plural = "Сессии"
