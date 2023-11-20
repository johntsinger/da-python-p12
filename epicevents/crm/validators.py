from django.core.exceptions import ValidationError
import re


def validate_phone(value):
    phone_regex = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'
    if not re.match(phone_regex, value):
        raise ValidationError(
            f"{value} is not a valid phone number"
        )
    return value
