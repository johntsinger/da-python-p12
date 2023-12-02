import typer
from cli.utils.validators import validate_value


def prompt_for(message, validator_name=None, ctx=None):
    new_value = None
    while new_value is None:
        new_value = typer.prompt(message.capitalize())
        if validator_name:
            new_value = validate_value(validator_name, new_value, ctx)
    return new_value
