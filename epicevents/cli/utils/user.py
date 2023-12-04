from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from cli.utils.token import Token, TokenNotFoundError


User = get_user_model()


def get_user():
    """Get current authenticated user"""
    try:
        token = Token().decode
    except (ExpiredSignatureError, TokenNotFoundError):
        return None
    try:
        return User.objects.get(id=token['user_id'])
    except ObjectDoesNotExist:
        return None
