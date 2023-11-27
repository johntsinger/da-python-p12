import typer
from typing_extensions import Annotated
from django.contrib.auth import get_user_model
from cli.utils.console import console
from cli.utils.validators import validate_callback
from cli.utils.table import create_table
from cli.utils.user import get_user, token_expired


User = get_user_model()
app = typer.Typer()


@app.command()
def list():
    user = get_user()
    if not user:
        token_expired()
    if user.has_perm('orm.view_user'):
        queryset = User.objects.all().exclude(is_superuser=True)
        table = create_table(queryset)
        if table.columns:
            console.print(table)
        else:
            console.print('[red]No user found.')
    else:
        console.print('[red]You are not allowed.')
