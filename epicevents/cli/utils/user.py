import typer
from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth import get_user_model
from cli.utils.token import Token, TokenNotFoundError
from cli.utils.console import console


User = get_user_model()


def permission_callback(ctx: typer.Context):
    command_name = ctx.info_name
    subcommand = ctx.invoked_subcommand

    if command_name == 'collaborator':
        command_name = 'user'
    user = get_user()
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        exit()
    if not user.has_perm(f'orm.{subcommand}_{command_name}'):
        console.print('[red]You are not allowed.')
        exit()


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
