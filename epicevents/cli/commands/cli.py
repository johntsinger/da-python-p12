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
    name='login'
)
app.add_typer(
    collaborator.app,
    name='collaborator',
    callback=permissions_callback
)
app.add_typer(
    client.app,
    name='client',
    callback=permissions_callback
)
app.add_typer(
    contract.app,
    name='contract',
    callback=permissions_callback
)
app.add_typer(
    event.app,
    name='event',
    callback=permissions_callback
)
