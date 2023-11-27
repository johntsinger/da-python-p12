import typer
from typing_extensions import Annotated
from cli.utils.console import console
from cli.utils.validators import validate_callback
from cli.utils.table import create_table
from orm.models import Client


app = typer.Typer()


@app.command()
def view():
    """
    View list of all clients.
    """
    queryset = Client.objects.all()
    table = create_table(queryset)
    if table.columns:
        console.print(table)
    else:
        console.print('[red]No client found.')
