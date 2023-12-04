import typer
from cli.utils.console import console
from cli.utils.user import get_user
from cli.utils.validators import validate


user = get_user()


def permissions_callback(ctx: typer.Context):
    """Callback to check general permissions"""
    command_name = ctx.info_name
    subcommand = ctx.invoked_subcommand

    if command_name == 'collaborator':
        command_name = 'user'
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        exit()
    if not user.has_perm(f'orm.{subcommand}_{command_name}'):
        console.print('[red]You are not allowed.')
        exit()


def validate_callback(
    ctx: typer.Context,
    params: typer.CallbackParam,
    value: str
):
    """Callback to validate value in typer.Option"""

    # callback called twice inside typer.Option
    # need model __str__ to validate second attempt
    ctx.user = user
    value, error = validate(params.name, value, ctx=ctx)
    if error:
        raise typer.BadParameter(
            typer.style(error, fg=typer.colors.RED)
        )
    return value


def allow_sales(value: str):
    """Allow sales department to filter contract"""
    if user.is_superuser or user.groups.first().name == 'sales':
        return value
    elif not value:
        return None
    console.print(
        "[red]Your are not allowed to use theses filters.\n"
        "Use --help to see options availlable"
    )
    raise typer.Exit()


def allow_management(value: str):
    """Allow management department to filter events"""
    if user.is_superuser or user.groups.first().name == 'management':
        return value
    elif not value:
        return None
    console.print(
        "[red][red]Your are not allowed to use theses filters.\n"
        "Use --help to see options availlable"
    )
    raise typer.Exit()


def allow_support(value: str):
    """Allow support department to filter"""
    if user.is_superuser or user.groups.first().name == 'support':
        return value
    elif not value:
        return None
    console.print(
        "[red]Your are not allowed to use theses filters.\n"
        "Use --help to see options availlable"
    )
    raise typer.Exit()
