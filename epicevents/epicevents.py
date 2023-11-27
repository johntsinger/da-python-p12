import typer
from cli.commands import (
    login,
    collaborator,
    client,
    contract,
    event
)


app = typer.Typer()
app.add_typer(login.app, name='login')
app.add_typer(collaborator.app, name='collaborator')
app.add_typer(client.app, name='client')
app.add_typer(contract.app, name='contract')
app.add_typer(event.app, name='event')


if __name__ == '__main__':
    app()
