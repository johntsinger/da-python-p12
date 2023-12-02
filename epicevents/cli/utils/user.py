from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth import get_user_model
from cli.utils.token import Token, TokenNotFoundError


User = get_user_model()


def get_user():
    try:
        token = Token().decode
    except (ExpiredSignatureError, TokenNotFoundError):
        return None
    if token['sub']:
        first_name, last_name = token['sub'].split()
    else:
        user = User.objects.get(id=token['user_id'])
        if not user.is_superuser:
            return None
        return user
    return User.objects.get(
        id=token['user_id'],
        first_name=first_name,
        last_name=last_name
    )
