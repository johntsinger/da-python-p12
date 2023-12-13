import os
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import Group
from typer.testing import CliRunner
from cli.commands.cli import app
from orm.models import User


class BaseTestCase(TestCase):
    runner = CliRunner()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.logout()

    @classmethod
    def create_superuser(cls):
        return User.objects.create_superuser(
            email='super@user.com',
            phone='0600000000',
            password='password',
        )

    @classmethod
    def create_user_sales(cls):
        return User.objects.create_user(
            first_name='user',
            last_name='sales',
            email='user@sales.com',
            phone='0611111111',
            password='password',
            department=Group.objects.get(name='sales')
        )

    @classmethod
    def create_user_management(cls):
        return User.objects.create_user(
            first_name='user',
            last_name='management',
            email='user@management.com',
            phone='0622222222',
            password='password',
            department=Group.objects.get(name='management')
        )

    @classmethod
    def logout(cls):
        os.environ.pop('TOKEN', None)

    @classmethod
    def login(cls, email):
        cls.runner.invoke(
            app,
            ['login'],
            input=f'{email}\npassword\n'
        )

    def token_expired(self):
        return 'Token has expired. Please log in again.'

    def not_allowed(self):
        return 'You are not allowed.'


class TestView(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = cls.create_superuser()

    def test_view_user_not_logged_in(self):
        self.logout()
        result = self.runner.invoke(
            app,
            ['collaborator', 'view']
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )
        self.login('super@user.com')

    def test_view_no_user_found(self):
        self.login('super@user.com')
        result = self.runner.invoke(
            app,
            ['collaborator', 'view']
        )
        self.assertIn(
            'No user found.',
            result.stdout
        )

    def test_view(self):
        self.login('super@user.com')
        user = self.create_user_sales()
        result = self.runner.invoke(
            app,
            ['collaborator', 'view']
        )
        self.assertIn(
            user.email,
            result.stdout
        )


class TestAdd(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.create_user_sales()
        cls.user_management = cls.create_user_management()

    def test_add_user_not_logged_in(self):
        self.logout()
        result = self.runner.invoke(
            app,
            ['collaborator', 'add']
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_add_user_not_allowed(self):
        self.login('user@sales.com')
        result = self.runner.invoke(
            app,
            ['collaborator', 'add'],
        )
        self.assertIn(
            self.not_allowed(),
            result.stdout
        )
        self.logout()

    def test_add(self):
        self.login('user@management.com')
        user_count = User.objects.count()
        result = self.runner.invoke(
            app,
            ['collaborator', 'add'],
            input=(
                'first_name\n'
                'last_name\n'
                'user@email.com\n'
                'password\n'
                'password\n'
                '0699999999\n'
                'sales\n'
            )
        )
        self.assertIn(
            'Collaborator successfully created.',
            result.stdout
        )
        self.assertEqual(
            user_count + 1,
            User.objects.count()
        )

    @patch('cli.commands.collaborator.get_user', return_value=None)
    def test_add_token_expired(self, mock):
        self.login('user@management.com')
        result = self.runner.invoke(
            app,
            ['collaborator', 'add'],
            input=(
                'first_name\n'
                'last_name\n'
                'user@email.com\n'
                'password\n'
                'password\n'
                '0699999999\n'
                'sales\n'
            )
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )


class TestChange(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.create_user_sales()
        cls.user_management = cls.create_user_management()
        cls.login('user@management.com')

    def test_change_invalid_user(self):
        result = self.runner.invoke(
            app,
            ['collaborator', 'change', 'invalid user'],
        )
        self.assertIn(
            'User not found',
            result.stdout
        )

    @patch('cli.commands.collaborator.get_user', return_value=None)
    def test_change_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['collaborator', 'change', 'user sales', '--all'],
            input=(
                'first_name\n'
                'last_name\n'
                'new@email.com\n'
                'password\n'
                'password\n'
                '0688888888\n'
                'support\n'
            )
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_change(self):
        result = self.runner.invoke(
            app,
            ['collaborator', 'change', 'user sales', '--all'],
            input=(
                'first_name\n'
                'last_name\n'
                'new@email.com\n'
                'password\n'
                'password\n'
                '0688888888\n'
                'support\n'
            )
        )
        self.assertIn(
            'User successfully updated.',
            result.stdout
        )


class TestDelete(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.create_user_sales()
        cls.user_management = cls.create_user_management()
        cls.login('user@management.com')

    def test_delete_invalid_user(self):
        result = self.runner.invoke(
            app,
            ['collaborator', 'delete', 'invalid user'],
        )
        self.assertIn(
            'User not found',
            result.stdout
        )

    def test_delete_abort(self):
        user_count = User.objects.count()
        result = self.runner.invoke(
            app,
            ['collaborator', 'delete', 'user sales'],
            input='n'
        )
        self.assertIn(
            'Aborted',
            result.stdout
        )
        self.assertEqual(
            user_count,
            User.objects.count()
        )

    @patch('cli.commands.collaborator.get_user', return_value=None)
    def test_delete_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['collaborator', 'delete', 'user sales'],
            input='y'
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_delete(self):
        user_count = User.objects.count()
        result = self.runner.invoke(
            app,
            ['collaborator', 'delete', 'user sales'],
            input='y'
        )
        self.assertIn(
            'Collaborator successfully deleted.',
            result.stdout
        )
        self.assertEqual(
            user_count - 1,
            User.objects.count()
        )
