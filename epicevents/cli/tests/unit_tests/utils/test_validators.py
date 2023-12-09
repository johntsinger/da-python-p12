from datetime import datetime, timedelta
import typer
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from orm.models import User, Compagny, Client, Contract, Event
from cli.utils import validators


class ParentContext:
    def __init__(self):
        self.info_name = None


class Context:
    def __init__(self):
        self.params = {}
        self.info_name = None
        self.user = None
        self.parent = ParentContext()


class ContextMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctx = Context()


class BaseTestCase(TestCase):
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
        compagny = Compagny.objects.create(name='compagny')
        cls.client_1 = Client.objects.create(
            first_name='client',
            last_name='test',
            email='client@test.com',
            phone='+33699999999',
            compagny=compagny,
            contact=cls.user_sales
        )
        cls.contract = Contract.objects.create(
            client=cls.client_1,
            price=100,
            balance=100,
            signed=True,
        )


class TestValidateDepartment(TestCase):
    management = 'management'
    sales = 'sales'
    support = 'support'
    invalid_department = 'invalid'

    def test_management_department_valid(self):
        group = validators.validate_department(self.management, ctx=None)
        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, self.management)

    def test_sales_department_valid(self):
        group = validators.validate_department(self.sales, ctx=None)
        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, self.sales)

    def test_support_department_valid(self):
        group = validators.validate_department(self.support, ctx=None)
        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, self.support)

    def test_validate_department_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_department,
            value=self.invalid_department,
            ctx=None
        )


class TestValidatePhone(BaseTestCase):
    phone = '0610101010'
    phone_normalized = '+33610101010'
    invalid_phone = '0615022222000323'
    existing_phone = '0611111111'

    def test_phone_valid(self):
        phone = validators.validate_phone(self.phone, ctx=None)
        self.assertEqual(phone, self.phone_normalized)

    def test_phone_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_phone,
            value=self.invalid_phone,
            ctx=None
        )

    def test_phone_already_exist(self):
        self.assertRaises(
            ValidationError,
            validators.validate_phone,
            value=self.existing_phone,
            ctx=None
        )


class TestValidateEmail(ContextMixin, BaseTestCase):
    email = 'email@test.com'
    invalid_email = 'test'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctx.info_name = 'collaborator'
        cls.existing_email = cls.user_sales.email

    def test_email_valid(self):
        email = validators.validate_email(self.email, ctx=self.ctx)
        self.assertEqual(email, self.email)

    def test_email_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_email,
            value=self.invalid_email,
            ctx=self.ctx
        )

    def test_email_already_exist(self):
        self.assertRaises(
            ValidationError,
            validators.validate_email,
            value=self.existing_email,
            ctx=self.ctx
        )


class TestValidatePassword(TestCase):
    password = 'password'
    invalid_password = 'invalid_password'

    def test_password_valid(self):
        with patch('typer.prompt', return_value=self.password):
            password = validators.validate_password(self.password, ctx=None)
            self.assertEqual(password, self.password)

    def test_password_invalid(self):
        with patch('typer.prompt', return_value=self.invalid_password):
            self.assertRaises(
                ValidationError,
                validators.validate_password,
                value=self.password,
                ctx=None
            )


class TestValidateDate(ContextMixin, TestCase):
    start_date = datetime.now() + timedelta(days=1)
    invalid_start_date = datetime.now() - timedelta(days=1)
    end_date = start_date + timedelta(hours=5)
    invalid_end_date = start_date - timedelta(hours=5)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctx.params['start_date'] = cls.start_date

    def test_start_date_valid(self):
        start_date = validators.validate_start_date(self.start_date, ctx=None)
        self.assertEqual(start_date, self.start_date)

    def test_start_date_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_start_date,
            value=self.invalid_start_date,
            ctx=None
        )

    def test_end_date_valid(self):
        end_date = validators.validate_end_date(self.end_date, ctx=self.ctx)
        self.assertEqual(end_date, self.end_date)

    def test_end_date_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_end_date,
            value=self.invalid_end_date,
            ctx=self.ctx
        )


class TestValidateCompagny(TestCase):
    compagny_name = 'test comp'

    def test_compagny_create(self):
        compagny_count = Compagny.objects.count()
        compagny = validators.validate_compagny(self.compagny_name, ctx=None)
        self.assertIsInstance(compagny, Compagny)
        self.assertEqual(compagny.name, self.compagny_name)
        self.assertEqual(
            Compagny.objects.count(),
            compagny_count + 1
        )

    def test_compagny_get(self):
        Compagny.objects.create(name=self.compagny_name)
        compagny_count = Compagny.objects.count()
        compagny = validators.validate_compagny(self.compagny_name, ctx=None)
        self.assertIsInstance(compagny, Compagny)
        self.assertEqual(compagny.name, self.compagny_name)
        self.assertEqual(
            Compagny.objects.count(),
            compagny_count
        )


class TestValidateContact(ContextMixin, BaseTestCase):
    contact_sales_name = 'user sales'
    contact_support_name = 'user support'
    invalid_contact_name = 'not existing'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(
            first_name='user',
            last_name='support',
            email='user@support.com',
            phone='0622222222',
            password='password',
            department=Group.objects.get(name='support')
        )

    def test_contact_name_valid_for_client(self):
        self.ctx.parent.info_name = 'client'
        contact = validators.validate_contact(
            self.contact_sales_name,
            ctx=self.ctx
        )
        self.assertIsInstance(contact, User)
        self.assertEqual(
            contact.get_full_name(),
            self.contact_sales_name
        )
        self.assertEqual(
            contact.groups.first().name,
            'sales'
        )

    def test_contact_name_not_existing_for_client(self):
        self.ctx.parent.info_name = 'client'
        self.assertRaises(
            ValidationError,
            validators.validate_contact,
            value=self.invalid_contact_name,
            ctx=self.ctx
        )

    def test_contact_name_valid_for_event(self):
        self.ctx.parent.info_name = 'event'
        contact = validators.validate_contact(
            self.contact_support_name,
            ctx=self.ctx
        )
        self.assertIsInstance(contact, User)
        self.assertEqual(
            contact.get_full_name(),
            self.contact_support_name
        )
        self.assertEqual(
            contact.groups.first().name,
            'support'
        )

    def test_contact_name_not_existing_for_event(self):
        self.ctx.parent.info_name = 'event'
        self.assertRaises(
            ValidationError,
            validators.validate_contact,
            value=self.invalid_contact_name,
            ctx=self.ctx
        )


class TestValidateClient(BaseTestCase):
    client_name = 'client test'
    invalid_client_name = 'not existing'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_client_name_valid(self):
        client = validators.validate_client(self.client_name, ctx=None)
        self.assertIsInstance(client, Client)
        self.assertEqual(
            f'{client.first_name} {client.last_name}',
            self.client_name
        )

    def test_client_name_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_client,
            value=self.invalid_client_name,
            ctx=None
        )


class TestValidateContract(ContextMixin, BaseTestCase):
    contract_uuid_invalid = '1554484-51513515'
    unexisting_contract_uuid = '7837d5ba-ede7-4f5c-893a-043591685854'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctx.user = cls.user_sales
        cls.contract_uuid = cls.contract.id

    def test_contract_uuid_valid(self):
        contract = validators.validate_contract(
            self.contract_uuid,
            ctx=self.ctx
        )
        self.assertIsInstance(contract, Contract)
        self.assertEqual(contract.id, self.contract_uuid)

    def test_contract_uuid_invalid(self):
        self.assertRaises(
            ValidationError,
            validators.validate_contract,
            value=self.contract_uuid_invalid,
            ctx=self.ctx
        )

    def test_contract_uuid_unexisting(self):
        self.assertRaises(
            ValidationError,
            validators.validate_contract,
            value=self.unexisting_contract_uuid,
            ctx=self.ctx
        )

    def test_not_client_contact_contract(self):
        user = User.objects.create_user(
            first_name='user',
            last_name='support',
            email='user@support.com',
            phone='0622222222',
            password='password',
            department=Group.objects.get(name='support')
        )
        self.ctx.user = user
        with patch(
            'cli.utils.console.console.print',
            return_value=(
                "Error: [red]You are not the contact of this client's contract"
            )
        ) as printing:
            self.assertRaises(
                typer.Exit,
                validators.validate_contract,
                value=self.contract_uuid,
                ctx=self.ctx
            )
            self.assertEqual(
                printing.return_value,
                "Error: [red]You are not the contact of this client's contract"
            )

    def test_contract_not_signed(self):
        self.contract.signed = False
        self.contract.save()

        with patch(
            'cli.utils.console.console.print',
            return_value=(
                "Error: [red]This contract has not yet been signed"
            )
        ) as printing:
            self.assertRaises(
                typer.Exit,
                validators.validate_contract,
                value=self.contract_uuid,
                ctx=self.ctx
            )
            self.assertEqual(
                printing.return_value,
                "Error: [red]This contract has not yet been signed"
            )

    def test_contract_already_have_event(self):
        Event.objects.create(
            name='event',
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=2),
            location='location',
            attendees=50,
            contract=self.contract,
            contact=None,
            note='note',
        )
        self.assertRaises(
            ValidationError,
            validators.validate_contract,
            value=self.contract_uuid,
            ctx=self.ctx
        )


class TestValidateUnique(TestCase):
    def unique_email(self):
        self.assertRaises(
            ValidationError,
            validators.validate_unique_email,
            value=self.user_sales.email,
        )

    def unique_phone(self):
        self.assertRaises(
            ValidationError,
            validators.validate_unique_phone,
            value=self.user_sales.phone,
        )

    def unique_event_for_contract(self):
        Event.objects.create(
            name='event',
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=2),
            location='location',
            attendees=50,
            contract=self.contract,
            contact=None,
            note='note',
        )
        self.assertRaises(
            ValidationError,
            validators.validate_unique_event_for_contract,
            value=self.contract.id,
        )


class TestValidate(TestCase):
    def test_return_value_if_key_error(self):
        value = validators.validate('first_name', 'john', ctx=None)
        self.assertIsInstance(value, tuple)
        self.assertEqual(
            value,
            ('john', None)
        )

    def test_return_value_if_validation_error(self):
        value = validators.validate('phone', '062222', ctx=None)
        self.assertIsInstance(value, tuple)
        self.assertEqual(
            value,
            (None, "Enter a valid phone number")
        )


class TestValidateValue(TestCase):
    def test_no_error(self):
        value = validators.validate_value('first_name', 'john', ctx=None)
        self.assertEqual(value, 'john')

    def test_error(self):
        with patch(
            'cli.utils.console.console.print',
            return_value=(
                "Enter a valid phone number"
            )
        ) as printing:
            value = validators.validate_value('phone', '062222', ctx=None)
            self.assertEqual(
                printing.return_value,
                "Enter a valid phone number"
            )
            self.assertEqual(value, None)
