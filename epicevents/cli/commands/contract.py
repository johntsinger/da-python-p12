import typer
from typing_extensions import Annotated
from cli.utils.console import console
from cli.utils.validators import validate_callback
from cli.utils.table import create_table
from cli.utils.user import get_user, token_expired
from orm.models import Contract


app = typer.Typer()


@app.command()
def list():
    user = get_user()
    if not user:
        token_expired()
    if user.has_perm('orm.view_contract'):
        queryset = Contract.objects.all()
        table = create_table(queryset)
        if table.columns:
            console.print(table)
        else:
            console.print('[red]No contract found.')
    else:
        console.print('[red]You are not allowed.')
