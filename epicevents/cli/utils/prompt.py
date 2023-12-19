import typer
from datetime import datetime
from cli.utils.validators import validate_value


def prompt_for(field_name, ctx):
    new_value = None
    if field_name == 'department':
        default = getattr(ctx.obj, 'groups').first()
    else:
        default = getattr(ctx.obj, field_name)
    if isinstance(default, datetime):
        default = default.strftime('%d-%m-%Y %H:%M')
    while new_value is None:
        if field_name == 'password':
            new_value = typer.prompt(field_name.capitalize())
        else:
            new_value = typer.prompt(
                field_name.capitalize(),
                default=str(default)
            )
        new_value = validate_value(field_name, new_value, ctx)
    return new_value
