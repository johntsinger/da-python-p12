import os
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import Group
from typer.testing import CliRunner
from guardian.shortcuts import assign_perm
from cli.commands.cli import app
from orm.models import User, Client, Compagny, Contract


class BaseTestCase(TestCase):
    runner = CliRunner()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.logout()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = User.objects.create_user(
            first_name='user',
            last_name='sales',
            email='user@sales.com',
            phone='0611111111',
            password='password',
            department=Group.objects.get(name='sales')
        )
        cls.user_management = User.objects.create_user(
            first_name='user',
            last_name='management',
            email='user@management.com',
            phone='0622222222',
            password='password',
            department=Group.objects.get(name='management')
        )
        compagny, created = Compagny.objects.get_or_create(
            name='test_compagny'
        )
        cls.client_1 = Client.objects.create(
            first_name='client',
            last_name='one',
            email='client@one.com',
            phone='0610101010',
            compagny=compagny,
            contact=cls.user_sales
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

    @classmethod
    def create_contract(cls):
        return Contract.objects.create(
            client=cls.client_1,
            price=100,
            balance=100,
            signed=False,
        )

    def token_expired(self):
        return 'Token has expired. Please log in again.'

    def not_allowed(self):
        return 'You are not allowed.'


class TestView(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login('user@management.com')

    @patch('cli.commands.contract.get_user', return_value=None)
    def test_view_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['contract', 'view']
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_view_no_contract(self):
        result = self.runner.invoke(
            app,
            ['contract', 'view']
        )
        self.assertIn(
            'No contract found.',
            result.stdout
        )

    def test_view(self):
        contract = self.create_contract()
        result = self.runner.invoke(
            app,
            ['contract', 'view']
        )
        self.assertIn(
            str(contract.id),
            result.stdout
        )

    def test_view_signed_not_signed_at_same_time(self):
        result = self.runner.invoke(
            app,
            ['contract', 'view', '-sn']
        )
        self.assertIn(
            'You can not use both signed and not signed at same time.',
            result.stdout
        )

    def test_view_paid_not_unpaid_at_same_time(self):
        result = self.runner.invoke(
            app,
            ['contract', 'view', '-pu']
        )
        self.assertIn(
            'You can not use both paid and unpaid at same time.',
            result.stdout
        )

    def test_view_filter(self):
        commands = ['-a', '-s', '-n', '-p', '-u']
        for command in commands:
            result = self.runner.invoke(
                app,
                ['contract', 'view', command]
            )
            with self.subTest(command=command):
                try:
                    self.assertIn(
                        'Contracts',
                        result.stdout
                    )
                except AssertionError:
                    self.assertIn(
                        'No contract found.',
                        result.stdout
                    )


class TestAdd(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login('user@management.com')

    def test_add(self):
        contract_count = Contract.objects.count()
        result = self.runner.invoke(
            app,
            ['contract', 'add'],
            input=(
                'client one\n'
                '100\n'
                'y\n'
            )
        )
        self.assertIn(
            'Contract successfully created.',
            result.stdout
        )
        self.assertEqual(
            contract_count + 1,
            Contract.objects.count()
        )

    @patch('cli.commands.contract.get_user', return_value=None)
    def test_add_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['contract', 'add'],
            input=(
                'client one\n'
                '100\n'
                'y\n'
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
        cls.contract = cls.create_contract()
        assign_perm('change_contract', cls.user_sales, cls.contract)
        cls.contract_2 = cls.create_contract()
        cls.login('user@sales.com')

    def test_change_invalid_uuid(self):
        result = self.runner.invoke(
            app,
            ['contract', 'change', 'invalid contract'],
        )
        self.assertIn(
            'is not a valid UUID.',
            result.stdout
        )

    def test_change_invalid_contract(self):
        result = self.runner.invoke(
            app,
            ['contract', 'change', 'aaaff048-78c6-45e2-83c3-1c85e82099eb'],
        )
        self.assertIn(
            'Contract not found.',
            result.stdout
        )

    @patch('cli.commands.contract.get_user', return_value=None)
    def test_change_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['contract', 'change', str(self.contract.id)]
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_change_not_allowed(self):
        result = self.runner.invoke(
            app,
            ['contract', 'change', str(self.contract_2.id)]
        )
        self.assertIn(
            'You are not allowed.',
            result.stdout
        )

    def test_change_missing_option(self):
        result = self.runner.invoke(
            app,
            ['contract', 'change', str(self.contract.id)],
        )
        self.assertIn(
            'Contract has not changed.'
            ' Specify options to change attributes.',
            result.stdout
        )

    def test_change(self):
        result = self.runner.invoke(
            app,
            ['contract', 'change', str(self.contract.id), '--all'],
            input=(
                'client one\n'
                '50\n'
                '10\n'
                'y\n'
            )
        )
        self.assertIn(
            'Contract successfully updated.',
            result.stdout
        )
