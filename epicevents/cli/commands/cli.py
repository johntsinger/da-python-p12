import typer
from cli.commands import (
    login,
    collaborator,
    client,
    contract,
    event
)
from cli.utils.callbacks import permissions_callback


app = typer.Typer()
app.add_typer(
    login.app,
    name='login',
    help="Login. Options are prompted if omitted."
)
app.add_typer(
    collaborator.app,
    name='collaborator',
    callback=permissions_callback,
    help="Collaborator commands."
)
app.add_typer(
    client.app,
    name='client',
    callback=permissions_callback,
    help="Client commands."
)
app.add_typer(
    contract.app,
    name='contract',
    callback=permissions_callback,
    help="Contract commands."
)
app.add_typer(
    event.app,
    name='event',
    callback=permissions_callback,
    help="Event commands."
)
