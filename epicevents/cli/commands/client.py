import typer
from typing import List
from typing_extensions import Annotated
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm, remove_perm
from orm.models import Client, Compagny
from cli.utils.console import console
from cli.utils.callbacks import validate_callback
from cli.utils.prompt import prompt_for
from cli.utils.table import create_table
from cli.utils.user import get_user


app = typer.Typer()

user = get_user()


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


@app.command()
def add(
    first_name: Annotated[
        str,
        typer.Option(
            "--first-name",
            prompt=True,
            help="Client's first name",
        )
    ],
    last_name: Annotated[
        str,
        typer.Option(
            "--last-name",
            prompt=True,
            help="Client's last name",
        )
    ],
    email: Annotated[
        str,
        typer.Option(
            "--email",
            prompt=True,
            help="Client's email address",
            callback=validate_callback,
        )
    ],
    phone: Annotated[
        str,
        typer.Option(
            "--phone",
            prompt=True,
            help="Client's phone number",
            callback=validate_callback
        )
    ],
    compagny: Annotated[
        str,
        typer.Option(
            "--compagny",
            prompt=True,
            help="Client's compagny name",
        )
    ]
):
    """
    Create a new client.
    Options are prompted if omitted.
    """
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        raise typer.Exit()
    compagny, created = Compagny.objects.get_or_create(
        name=compagny
    )
    new_client = Client.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        compagny=compagny,
        contact=user
    )
    assign_perm('change_client', user, new_client)
    console.print("[green]Client successfully created.")
    table = create_table(new_client)
    console.print(table)


@app.command()
def change(
    ctx: typer.Context,
    client: Annotated[
        List[str],
        typer.Argument(
            help="Full name of Client to be updated"
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
    phone: Annotated[
        bool,
        typer.Option(
            "--phone",
            "-p",
            help="Change phone number",
        )
    ] = False,
    compagny: Annotated[
        bool,
        typer.Option(
            "--compagny",
            "-y",
            help="Change compagny",
        )
    ] = False,
    contact: Annotated[
        bool,
        typer.Option(
            "--contact",
            "-c",
            help="Change contact",
        )
    ] = False,
    all_fields: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Change all fields. It's same as -flepyc",
        )
    ] = False,
):
    """
    Update a client.
    """
    try:
        client = Client.objects.annotate(
            full_name=Concat(
                'first_name',
                V(' '),
                'last_name'
            )
        ).get(
            full_name=' '.join(client)
        )
    except ObjectDoesNotExist:
        console.print("[red]Client not found.")
        raise typer.Exit()

    if not user.has_perm('change_client', client):
        console.print("[red]You are not allowed.")
        raise typer.Exit()

    fields_to_change = {}

    for key, value in ctx.params.items():
        if key in {"client", "all_fields"}:
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
            if key == 'contact':
                remove_perm('change_client', user, client)
                assign_perm('change_client', value, client)
            setattr(client, key, value)
        client.save()

    table = create_table(client)
    console.print(table)
