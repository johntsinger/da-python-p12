import typer
from cli.utils.console import console
from cli.utils.user import get_user
from cli.utils.validators import validate


def permissions_callback(ctx: typer.Context):
    """Callback to check general permissions"""
    command_name = ctx.info_name
    subcommand = ctx.invoked_subcommand

    user = get_user()

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
    user = get_user()
    ctx.user = user
    value, error = validate(params.name, value, ctx=ctx)
    if error:
        raise typer.BadParameter(
            typer.style(error, fg=typer.colors.RED)
        )
    return value
