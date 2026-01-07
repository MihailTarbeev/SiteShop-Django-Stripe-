from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Role, BusinessElement, AccessRoleRule

User = get_user_model()


class BasePermissionTestCase(TestCase):
    """Базовый класс для тестов системы доступа"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.items_element, _ = BusinessElement.objects.get_or_create(
            name='Items',
            defaults={'description': 'Товары'}
        )
        cls.users_element, _ = BusinessElement.objects.get_or_create(
            name='Users',
            defaults={'description': 'Пользователи'}
        )

        cls.admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={'description': 'Администратор'}
        )
        cls.user_role, _ = Role.objects.get_or_create(
            name='User',
            defaults={'description': 'Обычный пользователь'}
        )
        cls.manager_role, _ = Role.objects.get_or_create(
            name='Manager',
            defaults={'description': 'Менеджер'}
        )

        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=cls.admin_role
        )

        cls.regular_user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Regular',
            last_name='User',
            role=cls.user_role
        )

        cls.manager_user = User.objects.create_user(
            email='manager@test.com',
            password='testpass123',
            first_name='Manager',
            last_name='User',
            role=cls.manager_role
        )

        # Для обычного пользователя (User)
        AccessRoleRule.objects.get_or_create(
            role=cls.user_role,
            element=cls.users_element,
            defaults={
                'read_permission': True,      # Может читать свой профиль
                'read_all_permission': False,  # Не может читать всех
                'create_permission': False,   # Не может создавать пользователей
                'update_permission': True,    # Может обновлять свой профиль
                'update_all_permission': False,  # Не может обновлять всех
                'delete_permission': True,    # Может удалить свой аккаунт
                'delete_all_permission': False,  # Не может удалять чужие
            }
        )

        AccessRoleRule.objects.get_or_create(
            role=cls.user_role,
            element=cls.items_element,
            defaults={
                'read_permission': True,      # Может читать свои товары
                'read_all_permission': True,  # Может читать все товары
                'create_permission': False,   # Не может создавать товары
                'update_permission': False,   # Не может обновлять свои товары
                'update_all_permission': False,  # Не может обновлять все
                'delete_permission': False,   # Не может удалять свои товары
                'delete_all_permission': False,  # Не может удалять все
            }
        )

        # Для менеджера (Manager)
        AccessRoleRule.objects.get_or_create(
            role=cls.manager_role,
            element=cls.users_element,
            defaults={
                'read_permission': True,      # Может читать свой профиль
                'read_all_permission': False,  # Не может читать всех пользователей
                'create_permission': False,   # Не может создавать пользователей
                'update_permission': True,    # Может обновлять свой профиль
                'update_all_permission': False,  # Не может обновлять всех
                'delete_permission': True,    # Может удалить свой аккаунт
                'delete_all_permission': False,  # Не может удалять чужие
            }
        )

        AccessRoleRule.objects.get_or_create(
            role=cls.manager_role,
            element=cls.items_element,
            defaults={
                'read_permission': True,      # Может читать свои товары
                'read_all_permission': True,  # Может читать все товары
                'create_permission': True,    # Может создавать товары
                'update_permission': True,    # Может обновлять свои товары
                'update_all_permission': False,  # Не может обновлять чужие
                'delete_permission': True,    # Может удалять свои товары
                'delete_all_permission': False,  # Не может удалять чужие
            }
        )

        # Для администратора (Admin) - полный доступ ко всему
        AccessRoleRule.objects.get_or_create(
            role=cls.admin_role,
            element=cls.users_element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
                'update_all_permission': True,
                'delete_permission': True,
                'delete_all_permission': True,
            }
        )

        AccessRoleRule.objects.get_or_create(
            role=cls.admin_role,
            element=cls.items_element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
                'update_all_permission': True,
                'delete_permission': True,
                'delete_all_permission': True,
            }
        )
