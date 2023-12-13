from django.test import TestCase
from django.contrib.auth.models import Group
from typer.testing import CliRunner
from cli.commands.cli import app
from orm.models import User


class BaseTestCase(TestCase):
    runner = CliRunner()


class TestLogin(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(
            first_name='user',
            last_name='sales',
            email='user@sales.com',
            phone='0611111111',
            password='password',
            department=Group.objects.get(name='sales')
        )

    def test_login(self):
        result = self.runner.invoke(
            app,
            ['login'],
            input=f'user@sales.com\npassword\n'
        )
        self.assertIn(
            'Successfully logged in',
            result.stdout
        )

    def test_login_wrong_credential(self):
        result = self.runner.invoke(
            app,
            ['login'],
            input=f'user@sales.com\nwrong password\n'
        )
        self.assertIn(
            'Wrong email or password.',
            result.stdout
        )

    def test_bad_parameter(self):
        result = self.runner.invoke(
            app,
            ['login'],
            input=(
                'user\n'
                'user@sales.com\n'
                'wrong password\n'
            )
        )
        self.assertIn(
            'Error: Enter a valid email address.',
            result.stdout
        )
