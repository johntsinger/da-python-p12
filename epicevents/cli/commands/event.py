import typer
from typing_extensions import Annotated
from datetime import datetime
from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm, remove_perm
from orm.models import Event, Contract
from cli.utils.console import console
from cli.utils.callbacks import validate_callback
from cli.utils.table import create_table
from cli.utils.prompt import prompt_for
from cli.utils.user import get_user


app = typer.Typer()


@app.command()
def view(
    ctx: typer.Context,
    no_contact: Annotated[
        bool,
        typer.Option(
            "--no-contact",
            "-n",
            help="Filter event with no contact",
        )
    ] = False,
    assigned: Annotated[
        bool,
        typer.Option(
            "--assigned",
            "-a",
            help="Filter event assigned to me",
        )
    ] = False,
):
    """
    View list of all events.
    """
    user = get_user()
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        raise typer.Exit()

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

    if queryset:
        table = create_table(queryset)
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
            callback=validate_callback
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
            callback=validate_callback
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
    Required options are prompted if omitted.
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
        UUID,
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
    location: Annotated[
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
    contact: Annotated[
        bool,
        typer.Option(
            "--contact",
            "-c",
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
            help="Change all fields. It's same as -nselaco",
        )
    ] = False,
):
    """
    Update an event.
    """
    user = get_user()
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        raise typer.Exit()
    ctx.user = user

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

    ctx.obj = event
    fields_to_change = {}

    for key, value in ctx.params.items():
        if key in {"contract_id", "all_fields"}:
            continue
        if all_fields:
            value = True
        elif key == 'end_date' and not value and start_date:
            value = True
        if value:
            if key == 'note':
                fields_to_change[key] = typer.prompt(key, default='')
            else:
                if key == 'start_date' and not end_date:
                    ctx.end_date = event.end_date
                elif key == 'end_date' and not start_date:
                    ctx.start_date = event.start_date
                fields_to_change[key] = prompt_for(
                    field_name=key,
                    ctx=ctx
                )
                if key == 'start_date':
                    ctx.start_date = fields_to_change[key]

    if fields_to_change:
        for key, value in fields_to_change.items():
            if key == 'contact':
                if event.contact is not None:
                    remove_perm('change_event', event.contact, event)
                assign_perm('change_event', value, event)
            setattr(event, key, value)
        event.save()
        console.print('[green]Event successfully updated.')
    else:
        console.print(
            '[orange3]Event has not changed.'
            ' Specify options to change attributes.'
        )

    table = create_table(event)
    console.print(table)
