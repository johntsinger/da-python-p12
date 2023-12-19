import re
import typer
from datetime import datetime
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth.models import Group
from orm.models import User, Client, Compagny, Contract, Event
from orm.normalizers import normalize_phone, normalize_email
from cli.utils.console import console


def validate_value(validator_name, value, ctx):
    """Validate value when prompting outside of typer.Option"""
    value, error = validate(validator_name, value, ctx)
    if error:
        console.print(f'Error: [red]{error}')
        return None
    return value


def validate(validator_name, value, ctx):
    """Validator manager"""
    if not isinstance(value, datetime):
        value = value.strip()
    try:
        value = VALIDATORS[validator_name](value, ctx)
    except KeyError:
        pass
    except ValidationError as err:
        return None, err.message
    return value, None


def validate_unique_email(value, ctx):
    email = None
    if ctx.obj:
        email = ctx.obj.email
    if (
        email != value
        and (
            User.objects.filter(email=value).exists()
            or Client.objects.filter(email=value).exists()
        )
    ):
        raise ValidationError(
            "This email is already exists"
        )


def validate_unique_phone(value, ctx):
    phone = None
    if ctx.obj:
        phone = ctx.obj.phone
    if (
        phone != value
        and (
            User.objects.filter(phone=value).exists()
            or Client.objects.filter(phone=value).exists()
        )
    ):
        raise ValidationError(
            "This phone is already exists"
        )


def validate_unique_event_for_contract(value):
    if Event.objects.filter(contract=value).exists():
        raise ValidationError(
            'Event with this Contract already exists.'
        )


def validate_contract(value, ctx):
    try:
        contract = Contract.objects.get(id=value)
    except ObjectDoesNotExist:
        raise ValidationError(
            "Contract not found"
        )
    except ValidationError:
        raise ValidationError(
            f"{value} is not a valid contract ID"
        )
    if not contract.client.contact == ctx.user:
        console.print(
            "Error: [red]You are not the contact of this client's contract"
        )
        raise typer.Exit()
    if not contract.signed:
        console.print("Error: [red]This contract has not yet been signed")
        raise typer.Exit()
    validate_unique_event_for_contract(contract)
    return contract


def validate_client(value, ctx):
    try:
        client = Client.objects.annotate(
            full_name=Concat(
                'first_name',
                V(' '),
                'last_name'
            )
        ).get(
            full_name=value
        )
    except ObjectDoesNotExist:
        raise ValidationError(
            "Client not found"
        )
    return client


def validate_contact(value, ctx):
    if ctx.parent.info_name == 'client':
        group = 'sales'
    elif ctx.parent.info_name == 'event':
        group = 'support'
    try:
        contact = User.objects.annotate(
            full_name=Concat(
                'first_name',
                V(' '),
                'last_name'
            )
        ).get(
            full_name=value,
            groups__name=group
        )
    except ObjectDoesNotExist:
        raise ValidationError(
            "Contact not found"
        )
    return contact


def validate_compagny(value, ctx):
    # call only in prompt_for not in typer.Option
    # because callbacks are called twice
    compagny, created = Compagny.objects.get_or_create(
        name=value
    )
    return compagny


def format_date(value):
    formats = [
        "%d-%m-%Y %H:%M",
        "%d %m %Y %H:%M",
        "%d%m%Y %H:%M",
        "%d-%m-%Y %H",
        "%d %m %Y %H",
        "%d%m%Y %H",
    ]
    date = None
    for form in formats:
        try:
            date = datetime.strptime(value, form)
        except ValueError:
            pass
    if not date:
        raise ValidationError(
            f"{value} does not match the format"
            f" {', '.join(form for form in formats)}"
        )
    return date


def validate_start_date(value, ctx):
    if not isinstance(value, datetime):
        value = format_date(value)
    if datetime.now() > value:
        raise ValidationError(
            "Start date cannot be in the past"
        )
    if ctx.info_name == 'change' and value > ctx.end_date:
        raise ValidationError(
            "Start date cannot be after end date"
        )
    return value


def validate_end_date(value, ctx):
    if not isinstance(value, datetime):
        value = format_date(value)
    if ctx.info_name == 'change':
        start_date = ctx.start_date
    else:
        start_date = ctx.params.get('start_date', None)
    if value < start_date:
        raise ValidationError(
            "End date cannot be earlier than start date"
        )
    return value


def validate_password(value, ctx):
    confirmation = typer.prompt("Repeat for confirmation")
    if value != confirmation:
        raise ValidationError(
            "Error: The two entered values do not match."
        )
    return value


def validate_email(value, ctx):
    email_validator = EmailValidator()
    email_validator(value)
    value = normalize_email(value)
    if ctx.info_name != 'login':
        validate_unique_email(value, ctx)
    return value


def validate_phone(value, ctx):
    phone_regex = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'
    if not re.match(phone_regex, value):
        raise ValidationError(
            "Enter a valid phone number"
        )
    value = normalize_phone(value)
    validate_unique_phone(value, ctx)
    return value


def validate_department(value, ctx):
    if value not in {'management', 'sales', 'support'}:
        raise ValidationError(
            "Invalid department."
            " Department must be 'management', 'sales' or 'support'"
        )
    value = Group.objects.get(name=value)
    return value


VALIDATORS = {
    'email': validate_email,
    'phone': validate_phone,
    'department': validate_department,
    'password': validate_password,
    'contact': validate_contact,
    'compagny': validate_compagny,
    'client': validate_client,
    'contract': validate_contract,
    'start_date': validate_start_date,
    'end_date': validate_end_date,
}
