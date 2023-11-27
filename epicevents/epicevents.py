import typer
from cli.commands import (
    login,
    collaborator,
    client,
    contract,
    event
)
from cli.utils.user import permission_callback


app = typer.Typer()
app.add_typer(login.app, name='login')
app.add_typer(
    collaborator.app,
    name='collaborator',
    callback=permission_callback
)
app.add_typer(client.app, name='client', callback=permission_callback)
app.add_typer(contract.app, name='contract', callback=permission_callback)
app.add_typer(event.app, name='event', callback=permission_callback)


if __name__ == '__main__':
    app()
