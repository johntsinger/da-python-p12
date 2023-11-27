import typer
from typing_extensions import Annotated
from enum import Enum
from django.contrib.auth import get_user_model
from cli.utils.console import console
from cli.utils.validators import validate_callback
from cli.utils.table import create_table


User = get_user_model()
app = typer.Typer()


class Department(str, Enum):
    management = 'management',
    sales = 'sales',
    support = 'support'


@app.command()
def view():
    """
    View list of all collaborators.
    """
    queryset = User.objects.all().exclude(is_superuser=True)
    table = create_table(queryset)
    if table.columns:
        console.print(table)
    else:
        console.print('[red]No user found.')


@app.command()
def add(
    first_name: Annotated[
        str,
        typer.Option(
            "--first-name",
            prompt=True,
            help="Collaborator's first name",
        )
    ],
    last_name: Annotated[
        str,
        typer.Option(
            "--last-name",
            prompt=True,
            help="Collaborator's last name",
        )
    ],
    email: Annotated[
        str,
        typer.Option(
            "--email",
            prompt=True,
            help="Collaborator's email address",
            callback=validate_callback
        )
    ],
    password: Annotated[
        str,
        typer.Option(
            "--password",
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
            help="Collaborator's password"
        )
    ],
    phone: Annotated[
        str,
        typer.Option(
            "--phone",
            prompt=True,
            help="Collaborator's phone number",
            callback=validate_callback
        )
    ],
    department_name: Annotated[
        str,
        Department,
        typer.Option(
            "--department",
            prompt=True,
            help="Collaborator's department",
        )
    ]
):
    """
    Create a new collaborator.
    """
    new_user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        phone=phone,
        department_name=department_name
    )
    console.print('[green]Collaborator successfully created.')
    table = create_table(new_user)
    console.print(table)
