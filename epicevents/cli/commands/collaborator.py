import typer
from typing import List
from typing_extensions import Annotated
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from cli.utils.console import console
from cli.utils.callbacks import validate_callback
from cli.utils.prompt import prompt_for
from cli.utils.table import create_table


User = get_user_model()
app = typer.Typer()


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
        console.print("[red]No user found.")


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
            callback=validate_callback,
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
    department: Annotated[
        str,
        typer.Option(
            "--department",
            prompt="Department (management, sales, support)",
            help="Collaborator's department",
            callback=validate_callback
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
        department=department
    )
    console.print("[green]Collaborator successfully created.")
    table = create_table(new_user)
    console.print(table)


@app.command()
def change(
    ctx: typer.Context,
    collaborator: Annotated[
        List[str],
        typer.Argument(
            help="Full name of Collaborator to be updated"
        )
    ],
    first_name: Annotated[
        bool,
        typer.Option(
            "--first-name",
            "-f",
            help="Change first name",
        )
    ] = False,
    last_name: Annotated[
        bool,
        typer.Option(
            "--last-name",
            "-l",
            help="Change last name",
        )
    ] = False,
    email: Annotated[
        bool,
        typer.Option(
            "--email",
            "-e",
            help="Change email address",
        )
    ] = False,
    password: Annotated[
        bool,
        typer.Option(
            "--password",
            "-x",
            help="Change password"
        )
    ] = False,
    phone: Annotated[
        bool,
        typer.Option(
            "--phone",
            "-p",
            help="Change phone number",
        )
    ] = False,
    department: Annotated[
        bool,
        typer.Option(
            "--department",
            "-d",
            help="Change department",
        )
    ] = False,
    all_fields: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Change all fields. It's same as -flexpd",
        )
    ] = False,
):
    """
    Update a collaborator.
    """
    try:
        collaborator = User.objects.annotate(
            full_name=Concat(
                'first_name',
                V(' '),
                'last_name'
            )
        ).get(
            full_name=' '.join(collaborator)
        )
    except ObjectDoesNotExist:
        console.print("[red]User not found.")
        raise typer.Exit()

    fields_to_change = {}

    for key, value in ctx.params.items():
        if key in {"collaborator", "all_fields"}:
            continue
        if all_fields:
            value = True
        if value:
            fields_to_change[key] = prompt_for(
                message=key,
                validator_name=key,
                ctx=ctx
            )

    if fields_to_change:
        for key, value in fields_to_change.items():
            if key == "department":
                collaborator.groups.clear()
                collaborator.groups.add(value)
            elif key == "password":
                value = make_password(value)
            setattr(collaborator, key, value)
        collaborator.save()

    table = create_table(collaborator)
    console.print(table)
