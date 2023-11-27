import re
import typer
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


def validate_callback(
    ctx: typer.Context,
    param: typer.CallbackParam,
    value: str
):
    error = validate(param.name, value)
    if error:
        raise typer.BadParameter(
            typer.style(error, fg=typer.colors.RED)
        )
    return value


def validate(validator, value):
    try:
        VALIDATORS[validator](value)
    except ValidationError as err:
        # console.print(f"[red]{err.message}")
        return err.message
    return None


def validate_phone(value):
    phone_regex = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'
    if not re.match(phone_regex, value):
        raise ValidationError(
            f"{value} is not a valid phone number"
        )


VALIDATORS = {
    'email': EmailValidator(),
    'phone': validate_phone,
}
