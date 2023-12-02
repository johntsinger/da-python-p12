import re
import typer
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth.models import Group
from orm.models import User, Client, Compagny
from orm.normalizers import normalize_phone, normalize_email
from cli.utils.console import console


def validate_value(validator_name, value, ctx):
    value, error = validate(validator_name, value, ctx)
    if error:
        console.print(f'Error: [red]{error}')
        return None
    return value


def validate(validator_name, value, ctx):
    try:
        value = VALIDATORS[validator_name](value, ctx)
    except KeyError:
        pass
    except ValidationError as err:
        return None, err.message
    return value, None


def validate_unique(key, value):
    if (
        User.objects.filter(**{key: value}).exists()
        or Client.objects.filter(**{key: value}).exists()
    ):
        raise ValidationError(
            f"This {key} is already exists"
        )


def validate_contact(value, ctx):
    if ctx.parent.info_name == 'client':
        group = 'sales'
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
        validate_unique('email', value)
    return value


def validate_phone(value, ctx):
    phone_regex = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'
    if not re.match(phone_regex, value):
        raise ValidationError(
            f"Enter a valid phone number"
        )
    value = normalize_phone(value)
    validate_unique('phone', value)
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
    'compagny': validate_compagny
}
