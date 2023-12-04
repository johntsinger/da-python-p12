import typer
from typing_extensions import Annotated
from datetime import datetime, timedelta, timezone
from django.contrib.auth import authenticate
from cli.utils.console import console
from cli.utils.callbacks import validate_callback
from cli.utils.token import NewToken


app = typer.Typer()


@app.callback(invoke_without_command=True)
def login(
    email: Annotated[
        str,
        typer.Option(
            "--email",
            "-e",
            prompt=True,
            help="Your email address",
            callback=validate_callback
        )
    ],
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            prompt=True,
            hide_input=True,
            help='Your password'
        )
    ]
):
    """Login."""
    user = authenticate(username=email, password=password)
    if user is not None:
        payload = {
            'user_id': user.id,
            'sub': user.get_full_name(),
            'iss': 'epicevents_crm',
            'exp': datetime.now(tz=timezone.utc) + timedelta(hours=12)
        }
        NewToken(payload)
        console.print('[green]Successfully logged in')
    else:
        console.print("[red]Wrong email or password.")
