from django.test import TestCase
from django.contrib.auth.models import Group
from orm.models import User


class TestUserManager(TestCase):
    group = Group.objects.get(name='sales')

    def test_create_user_missing_email(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='',
            first_name='first_name',
            last_name='last_name',
            phone='phone',
            password='password',
            department=self.group
        )

    def test_create_user_missing_first_name(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='test@test.com',
            first_name='',
            last_name='last_name',
            phone='phone',
            password='password',
            department=self.group
        )

    def test_create_user_missing_last_name(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='test@test.com',
            first_name='first_name',
            last_name='',
            phone='phone',
            password='password',
            department=self.group
        )

    def test_create_user_missing_phone(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='test@test.com',
            first_name='first_name',
            last_name='last_name',
            phone='',
            password='password',
            department=self.group
        )

    def test_create_user_missing_password(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='test@test.com',
            first_name='first_name',
            last_name='last_name',
            phone='phone',
            password='',
            department=self.group
        )

    def test_create_user_missing_department(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            email='test@test.com',
            first_name='first_name',
            last_name='last_name',
            phone='phone',
            password='password',
            department=None
        )

    def test_create_user(self):
        user_count = User.objects.count()
        user = User.objects.create_user(
            email='test@test.com',
            first_name='first_name',
            last_name='last_name',
            phone='phone',
            password='password',
            department=self.group
        )
        self.assertEqual(user_count + 1, User.objects.count())
        self.assertFalse(user.is_superuser)

    def test_create_superuser_missing_password(self):
        self.assertRaises(
            ValueError,
            User.objects.create_superuser,
            email='test@test.com',
            phone='phone',
            password='',
        )

    def test_create_superuser(self):
        user_count = User.objects.count()
        user = User.objects.create_superuser(
            email='test@test.com',
            phone='phone',
            password='password',
        )
        self.assertEqual(user_count + 1, User.objects.count())
        self.assertTrue(user.is_superuser)
