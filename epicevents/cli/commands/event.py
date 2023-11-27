import typer
from typing_extensions import Annotated
from cli.utils.console import console
from cli.utils.validators import validate_callback
from cli.utils.table import create_table
from orm.models import Event


app = typer.Typer()


@app.command()
def list():
    """
    View list of all events.
    """
    queryset = Event.objects.all()
    table = create_table(queryset)
    if table.columns:
        console.print(table)
    else:
        console.print('[red]No event found.')
