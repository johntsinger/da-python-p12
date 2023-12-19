import os
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import Group
from typer.testing import CliRunner
from guardian.shortcuts import assign_perm
from cli.commands.cli import app
from orm.models import User, Client, Compagny


class BaseTestCase(TestCase):
    runner = CliRunner()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.logout()

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
    def create_client(cls, contact):
        compagny, created = Compagny.objects.get_or_create(
            name='test_compagny'
        )
        return Client.objects.create(
            first_name='client',
            last_name='one',
            email='client@one.com',
            phone='0610101010',
            compagny=compagny,
            contact=contact
        )

    @classmethod
    def create_client_2(cls, contact):
        compagny, created = Compagny.objects.get_or_create(
            name='test_compagny'
        )
        return Client.objects.create(
            first_name='client',
            last_name='two',
            email='client@two.com',
            phone='0620202020',
            compagny=compagny,
            contact=contact
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


class TestView(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.create_user_sales()
        cls.login('user@sales.com')

    def test_view_no_client(self):
        result = self.runner.invoke(
            app,
            ['client', 'view']
        )
        self.assertIn(
            'No client found.',
            result.stdout
        )

    def test_view(self):
        client = self.create_client(self.user_sales)
        result = self.runner.invoke(
            app,
            ['client', 'view']
        )
        self.assertIn(
            client.email,
            result.stdout
        )


class TestAdd(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.create_user_sales()
        cls.login('user@sales.com')

    def test_add(self):
        self.login('user@sales.com')
        client_count = Client.objects.count()
        result = self.runner.invoke(
            app,
            ['client', 'add'],
            input=(
                'first_name\n'
                'last_name\n'
                'client@email.com\n'
                '0610101010\n'
                'new compagny\n'
                'user sales\n'
            )
        )
        self.assertIn(
            'Client successfully created.',
            result.stdout
        )
        self.assertEqual(
            client_count + 1,
            Client.objects.count()
        )

    @patch('cli.commands.client.get_user', return_value=None)
    def test_add_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['client', 'add'],
            input=(
                'first_name\n'
                'last_name\n'
                'client@email.com\n'
                '0610101010\n'
                'new compagny\n'
                'user sales\n'
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
        cls.client = cls.create_client(cls.user_sales)
        cls.client_2 = cls.create_client_2(cls.user_sales)
        assign_perm('change_client', cls.user_sales, cls.client)
        cls.login('user@sales.com')

    def test_change_invalid_client(self):
        result = self.runner.invoke(
            app,
            ['client', 'change', 'invalid client'],
        )
        self.assertIn(
            'Client not found',
            result.stdout
        )

    @patch('cli.commands.client.get_user', return_value=None)
    def test_change_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['client', 'change', 'client one'],
            input=(
                'first_name\n'
                'last_name\n'
                'client@email.com\n'
                '0610101010\n'
                'new compagny\n'
                'user sales\n'
            )
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_change_not_allowed(self):
        result = self.runner.invoke(
            app,
            ['client', 'change', 'client two', '--all'],
            input=(
                'first_name\n'
                'last_name\n'
                'client@email.com\n'
                '0610101010\n'
                'new compagny\n'
                'user sales\n'
            )
        )
        self.assertIn(
            'You are not allowed.',
            result.stdout
        )
        self.login('user@sales.com')

    def test_change_missing_option(self):
        result = self.runner.invoke(
            app,
            ['client', 'change', 'client one'],
        )
        self.assertIn(
            'Client has not changed.'
            ' Specify options to change attributes.',
            result.stdout
        )

    def test_change(self):
        result = self.runner.invoke(
            app,
            ['client', 'change', 'client one', '--all'],
            input=(
                'first_name\n'
                'last_name\n'
                'client@email.com\n'
                '0610101010\n'
                'new compagny\n'
                'user sales\n'
            )
        )
        self.assertIn(
            'Client successfully updated.',
            result.stdout
        )
