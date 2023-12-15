import os
from datetime import datetime
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import Group
from typer.testing import CliRunner
from guardian.shortcuts import assign_perm
from cli.commands.cli import app
from orm.models import (
    User,
    Client,
    Compagny,
    Contract,
    Event
)


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
        cls.user_support = User.objects.create_user(
            first_name='user',
            last_name='support',
            email='user@support.com',
            phone='0633333333',
            password='password',
            department=Group.objects.get(name='support')
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
        cls.client_2 = Client.objects.create(
            first_name='client',
            last_name='two',
            email='client@two.com',
            phone='0620202020',
            compagny=compagny,
            contact=cls.user_sales
        )
        cls.contract_signed = Contract.objects.create(
            client=cls.client_1,
            price=100,
            balance=100,
            signed=True,
        )
        cls.contract_signed_2 = Contract.objects.create(
            client=cls.client_2,
            price=100,
            balance=100,
            signed=True,
        )
        cls.contract_signed_3 = Contract.objects.create(
            client=cls.client_1,
            price=100,
            balance=100,
            signed=True,
        )
        cls.contract_not_signed = Contract.objects.create(
            client=cls.client_1,
            price=100,
            balance=100,
            signed=False,
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
    def create_event(cls):
        return Event.objects.create(
            name='test event',
            start_date=datetime(2024, 1, 10, hour=10),
            end_date=datetime(2024, 1, 10, hour=18),
            location='address',
            attendees=80,
            contract=cls.contract_signed,
            contact=cls.user_support,
            note='test event',
        )

    @classmethod
    def create_event_2(cls):
        return Event.objects.create(
            name='test event',
            start_date=datetime(2024, 1, 10, hour=10),
            end_date=datetime(2024, 1, 10, hour=18),
            location='address',
            attendees=80,
            contract=cls.contract_signed_2,
            contact=None,
            note='test event',
        )

    def token_expired(self):
        return 'Token has expired. Please log in again.'

    def not_allowed(self):
        return 'You are not allowed.'


class TestView(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login('user@support.com')

    @patch('cli.commands.event.get_user', return_value=None)
    def test_view_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['event', 'view']
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_view_no_event(self):
        result = self.runner.invoke(
            app,
            ['event', 'view']
        )
        self.assertIn(
            'No event found.',
            result.stdout
        )

    def test_view(self):
        event = self.create_event()
        result = self.runner.invoke(
            app,
            ['event', 'view']
        )
        self.assertIn(
            str(event.contract.id),
            result.stdout
        )

    def test_view_filter(self):
        commands = ['-a', '-n']
        for command in commands:
            result = self.runner.invoke(
                app,
                ['event', 'view', command]
            )
            with self.subTest(command=command):
                try:
                    self.assertIn(
                        'Events',
                        result.stdout
                    )
                except AssertionError:
                    self.assertIn(
                        'No event found.',
                        result.stdout
                    )


class TestAdd(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login('user@sales.com')

    def test_add(self):
        event_count = Event.objects.count()
        result = self.runner.invoke(
            app,
            ['event', 'add'],
            input=(
                f'{self.contract_signed.id}\n'
                'test event\n'
                '10 01 2024 10\n'
                '10 01 2024 18\n'
                'test address\n'
                '80\n'
                'user support\n'
                'test note'
            )
        )
        self.assertIn(
            'Event successfully created.',
            result.stdout
        )
        self.assertEqual(
            event_count + 1,
            Event.objects.count()
        )


class TestChange(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.create_event()
        assign_perm('change_event', cls.user_support, cls.event)
        cls.event_2 = cls.create_event_2()
        cls.login('user@support.com')

    def test_change_invalid_uuid(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', 'invalid event'],
        )
        self.assertIn(
            'is not a valid UUID.',
            result.stdout
        )

    def test_change_invalid_contract(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', 'aaaff048-78c6-45e2-83c3-1c85e82099eb'],
        )
        self.assertIn(
            'Event not found.',
            result.stdout
        )

    @patch('cli.commands.event.get_user', return_value=None)
    def test_change_token_expired(self, mock):
        result = self.runner.invoke(
            app,
            ['event', 'change', str(self.event.contract.id)]
        )
        self.assertIn(
            self.token_expired(),
            result.stdout
        )

    def test_change_not_allowed(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', str(self.event_2.contract.id)]
        )
        self.assertIn(
            'You are not allowed.',
            result.stdout
        )

    def test_change_missing_option(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', str(self.event.contract.id)],
        )
        self.assertIn(
            'Event has not changed.'
            ' Specify options to change attributes.',
            result.stdout
        )

    def test_change(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', str(self.event.contract.id), '--all'],
            input=(
                'test event\n'
                '10 01 2024 10\n'
                '10 01 2024 18\n'
                'test address\n'
                '80\n'
                'user support\n'
                'test note\n'
            )
        )
        self.assertIn(
            'Event successfully updated.',
            result.stdout
        )

    def test_change_start_date_without_end_date(self):
        result = self.runner.invoke(
            app,
            ['event', 'change', str(self.event.contract.id), '-s'],
            input=(
                '10 01 2024 10\n'
                '10 01 2024 18\n'
            )
        )
        self.assertIn(
            'Event successfully updated.',
            result.stdout
        )
