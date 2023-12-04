import typer
from typing_extensions import Annotated
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm, remove_perm
from orm.models import Event, Contract
from cli.utils.console import console
from cli.utils.callbacks import (
    validate_callback,
    allow_management,
    allow_support
)
from cli.utils.table import create_table
from cli.utils.prompt import prompt_for
from cli.utils.user import get_user


app = typer.Typer()

user = get_user()


def management():
    """Display options for management department"""
    if not user:
        return True
    if user.is_superuser or user.groups.first().name == 'management':
        return False
    return True


def support():
    """Display options for support department"""
    if not user:
        return True
    if user.is_superuser or user.groups.first().name == 'support':
        return False
    return True


@app.command()
def view(
    ctx: typer.Context,
    no_contact: Annotated[
        bool,
        typer.Option(
            "--no-contact",
            "-n",
            help="Filter event with no contact",
            callback=allow_management,
            hidden=management()
        )
    ] = False,
    assigned: Annotated[
        bool,
        typer.Option(
            "--assigned",
            "-a",
            help="Filter event assigned to me",
            callback=allow_support,
            hidden=support()
        )
    ] = False,
):
    """
    View list of all events.
    """
    querydict = {}
    for key, value in ctx.params.items():
        if value:
            if key == 'no_contact':
                querydict['contact'] = None
            elif key == 'assigned':
                querydict['contact'] = user
    if querydict:
        queryset = Event.objects.filter(**querydict)
    else:
        queryset = Event.objects.all()

    table = create_table(queryset)
    if table.columns:
        console.print(table)
    else:
        console.print('[red]No event found.')


@app.command()
def add(
    contract: Annotated[
        str,
        typer.Option(
            "--contract",
            prompt=True,
            help="Event's contract",
            callback=validate_callback
        )
    ],
    name: Annotated[
        str,
        typer.Option(
            "--name",
            prompt=True,
            help="Event's name",
        )
    ],
    start_date: Annotated[
        datetime,
        typer.Option(
            "--start",
            prompt=True,
            formats=[
                "%d-%m-%Y %H:%M",
                "%d %m %Y %H:%M",
                "%d%m%Y %H:%M",
                "%d-%m-%Y %H",
                "%d %m %Y %H",
                "%d%m%Y %H",
            ],
            help="Event's start date",
        )
    ],
    end_date: Annotated[
        datetime,
        typer.Option(
            "--end",
            prompt=True,
            formats=[
                "%d-%m-%Y %H:%M",
                "%d %m %Y %H:%M",
                "%d%m%Y %H:%M",
                "%d-%m-%Y %H",
                "%d %m %Y %H",
                "%d%m%Y %H",
            ],
            help="Event's end date",
        )
    ],
    location: Annotated[
        str,
        typer.Option(
            "--location",
            prompt=True,
            help="Event's location",
        )
    ],
    attendees: Annotated[
        int,
        typer.Option(
            "--attendees",
            prompt=True,
            help="Event's number of attendees",
        )
    ],
    note: Annotated[
        str,
        typer.Option(
            "--note",
            prompt=True,
            help="Event's note",
        )
    ] = "",
):
    """
    Create a new event.
    Options are prompted if omitted.
    """
    new_event = Event.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        location=location,
        attendees=attendees,
        contract=contract,
        contact=None,
        note=note,
    )
    console.print("[green]Event successfully created.")
    table = create_table(new_event)
    console.print(table)


@app.command()
def change(
    ctx: typer.Context,
    contract_id: Annotated[
        str,
        typer.Argument(
            help="Event's contract id"
        )
    ],
    name: Annotated[
        bool,
        typer.Option(
            "--name",
            "-n",
            help="Change name",
        )
    ] = False,
    start_date: Annotated[
        bool,
        typer.Option(
            "--start",
            "-s",
            help="Change start date",
        )
    ] = False,
    end_date: Annotated[
        bool,
        typer.Option(
            "--end",
            "-e",
            help="Change end date",
        )
    ] = False,
    localisation: Annotated[
        bool,
        typer.Option(
            "--localisation",
            "-l",
            help="Change localisation",
        )
    ] = False,
    attendees: Annotated[
        bool,
        typer.Option(
            "--attendees",
            "-a",
            help="Change number of attendees",
        )
    ] = False,
    contract: Annotated[
        bool,
        typer.Option(
            "--contract",
            "-c",
            help="Change contract",
        )
    ] = False,
    contact: Annotated[
        bool,
        typer.Option(
            "--contact",
            "-u",
            help="Change contact",
        )
    ] = False,
    note: Annotated[
        bool,
        typer.Option(
            "--note",
            "-o",
            help="Change note",
        )
    ] = False,
    all_fields: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Change all fields. It's same as -nselacuo",
        )
    ] = False,
):
    """
    Update an event.
    """
    try:
        event = Contract.objects.get(id=contract_id).event
    except ObjectDoesNotExist:
        console.print("[red]Event not found.")
        raise typer.Exit()

    if (
        user.groups.first().name != 'management'
        and not user.has_perm('change_event', event)
    ):
        console.print("[red]You are not allowed.")
        raise typer.Exit()

    fields_to_change = {}

    for key, value in ctx.params.items():
        if key in {"contract_id", "all_fields"}:
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
                remove_perm('change_event', event.contact, event)
                assign_perm('change_event', value, event)
            setattr(event, key, value)
        event.save()

    table = create_table(event)
    console.print(table)
