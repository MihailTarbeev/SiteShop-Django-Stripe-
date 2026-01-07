from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Item, Category
from .base import BasePermissionTestCase

User = get_user_model()


class ItemViewPermissionTest(BasePermissionTestCase):
    def setUp(self):
        super().setUp()

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.item_regular_user = Item.objects.create(
            name='Item Regular User',
            price=100,
            owner=self.regular_user,
            category=self.category,
            slug='item-regular-user',
            is_available=True
        )

        self.item_manager_user = Item.objects.create(
            name='Item Manager User',
            price=200,
            owner=self.manager_user,
            category=self.category,
            slug='item-manager-user',
            is_available=True
        )

        self.item_admin_user = Item.objects.create(
            name='Item Admin User',
            price=300,
            owner=self.admin_user,
            category=self.category,
            slug='item-admin-user',
            is_available=True
        )

    def test_people_home_view_access(self):
        """Тест доступа к главной странице товаров"""
        url = reverse('home')

        # Обычный пользователь может видеть все товары
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Item Regular User')
        self.assertContains(response, 'Item Manager User')
        self.assertContains(response, 'Item Admin User')

        # Менеджер также может видеть все товары
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Админ также может видеть все товары
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_show_item_view_permissions(self):
        """Тест доступа к просмотру конкретного товара"""

        # Обычный пользователь может просматривать любой товар
        url = reverse('item', kwargs={'item_slug': 'item-manager-user'})
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Менеджер может просматривать любой товар
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Админ может просматривать любой товар
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_item_view_permissions(self):
        """Тест доступа к редактированию товара"""

        # User НЕ может редактировать свой товар
        url = reverse('edit_item', kwargs={'slug': 'item-regular-user'})
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Менеджер может редактировать только СВОИ товары
        url = reverse('edit_item', kwargs={'slug': 'item-manager-user'})
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Менеджер НЕ может редактировать ЧУЖИЕ товары
        url = reverse('edit_item', kwargs={'slug': 'item-regular-user'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Админ может редактировать ЛЮБЫЕ товары
        url = reverse('edit_item', kwargs={'slug': 'item-regular-user'})
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_item_view_permissions(self):
        """Тест доступа к удалению товара"""

        # Обычный пользователь НЕ может удалять товары
        url = reverse('delete_item', kwargs={'slug': 'item-regular-user'})
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Менеджер может удалять только СВОИ товары
        url = reverse('delete_item', kwargs={'slug': 'item-manager-user'})
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Свой товар - доступ есть

        # Менеджер НЕ может удалять ЧУЖИЕ товары
        url = reverse('delete_item', kwargs={'slug': 'item-regular-user'})
        response = self.client.get(url)
        # Чужой товар - нет доступа
        self.assertEqual(response.status_code, 403)

        # Админ может удалять ЛЮБЫЕ товары
        url = reverse('delete_item', kwargs={'slug': 'item-regular-user'})
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        # Может удалять чужой товар
        self.assertEqual(response.status_code, 200)

    def test_create_item_view_permission(self):
        """Тест доступа к созданию товара"""
        url = reverse('add_item')

        # Обычный пользователь НЕ может создавать товары
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Менеджер может создавать товары
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Админ может создавать товары
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_access_permissions(self):
        """Тест доступа к профилям пользователей"""

        url_own_profile = reverse('users:profile')

        # Обычный пользователь может видеть и редактировать только СВОЙ профиль
        self.client.login(email='user@test.com', password='testpass123')

        response = self.client.get(url_own_profile)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user@test.com')
        self.assertContains(response, 'Профиль пользователя')

        # Проверяем, что может обновить свой профиль
        update_data = {
            'first_name': 'ОбновленноеИмя',
            'last_name': 'ОбновленнаяФамилия',
            'email': 'user@test.com',
        }
        response = self.client.post(
            url_own_profile, data=update_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'ОбновленноеИмя')

        # Проверяем, что менеджер не может управлять другими пользователями
        self.client.login(email='manager@test.com', password='testpass123')

        # Доступ к своему профилю
        response = self.client.get(url_own_profile)
        self.assertEqual(response.status_code, 200)

        # Менеджер не должен иметь доступ к админке пользователей
        # Проверяем через права
        self.assertFalse(self.manager_user.has_permission_field(
            'Users', 'read_all_permission'))
        self.assertFalse(self.manager_user.has_permission_field(
            'Users', 'update_all_permission'))
        self.assertFalse(self.manager_user.has_permission_field(
            'Users', 'delete_all_permission'))

        # Админ может управлять всеми пользователями
        self.client.login(email='admin@test.com', password='testpass123')

        # Доступ к своему профилю
        response = self.client.get(url_own_profile)
        self.assertEqual(response.status_code, 200)

        # Проверяем создание пользователей
        url_register = reverse('users:register')
        response = self.client.get(url_register)
        self.assertEqual(response.status_code, 200)

    def test_shop_category_view_access(self):
        """Тест доступа к категориям товаров"""
        url = reverse('category', kwargs={'cat_slug': 'test-category'})

        # Обычный пользователь может просматривать категории
        self.client.login(email='user@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Менеджер может просматривать категории
        self.client.login(email='manager@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Админ может просматривать категории
        self.client.login(email='admin@test.com', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
