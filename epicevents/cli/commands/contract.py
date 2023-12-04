import typer
from typing_extensions import Annotated
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import assign_perm, remove_perm
from uuid import UUID
from cli.utils.console import console
from cli.utils.callbacks import validate_callback, allow_sales
from cli.utils.prompt import prompt_for
from cli.utils.table import create_table
from cli.utils.user import get_user
from orm.models import Contract


app = typer.Typer()

user = get_user()


def sales():
    """Display options for sales department"""
    if user.is_superuser or user.groups.first().name == 'sales':
        return False
    return True


@app.command()
def view(
    ctx: typer.Context,
    assigned: Annotated[
        bool,
        typer.Option(
            "--assigned",
            "-a",
            help="Filter contract assigned to me",
            callback=allow_sales,
            hidden=sales()
        )
    ] = False,
    signed: Annotated[
        bool,
        typer.Option(
            "--signed",
            "-s",
            help="Filter contract signed",
            callback=allow_sales,
            hidden=sales()
        )
    ] = False,
    not_signed: Annotated[
        bool,
        typer.Option(
            "--not-signed",
            "-n",
            help="Filter contract not signed",
            callback=allow_sales,
            hidden=sales()
        )
    ] = False,
    paid: Annotated[
        bool,
        typer.Option(
            "--paid",
            "-p",
            help="Filter contract paid",
            callback=allow_sales,
            hidden=sales()
        )
    ] = False,
    unpaid: Annotated[
        bool,
        typer.Option(
            "--unpaid",
            "-u",
            help="Filter contract unpaid",
            callback=allow_sales,
            hidden=sales()
        )
    ] = False,
):
    """
    View list of all contract.
    """
    if signed and not_signed:
        raise typer.BadParameter(
            'You can not use both signed and not signed at same time.'
            ' Please choose only one of them.'
            ' If you need both use neither of them.'
        )
    if paid and unpaid:
        raise typer.BadParameter(
            'You can not use both paid and unpaid at same time.'
            ' Please choose only one of them.'
            ' If you need both use neither of them.'
        )
    querydict = {}
    for key, value in ctx.params.items():
        if value:
            if key == 'assigned':
                querydict['client__contact'] = user
            elif key == 'signed':
                querydict['signed'] = True
            elif key == 'not_signed':
                querydict['signed'] = False
            elif key == 'paid':
                querydict['balance'] = 0
            elif key == 'unpaid':
                querydict['balance__gt'] = 0
    if querydict:
        queryset = Contract.objects.filter(**querydict)
    else:
        queryset = Contract.objects.all()

    table = create_table(queryset)
    if table.columns:
        console.print(table)
    else:
        console.print('[red]No contract found.')


@app.command()
def add(
    client: Annotated[
        str,
        typer.Option(
            "--client",
            prompt=True,
            help="Contract's client full name",
            callback=validate_callback
        )
    ],
    price: Annotated[
        float,
        typer.Option(
            "--price",
            prompt=True,
            help="Contract's price",
            min=0
        )
    ],
):
    """
    Create a new contract.
    """
    if not user:
        console.print('[red]Token has expired. Please log in again.')
        raise typer.Exit()
    signed = typer.confirm('Contract signed ?')
    new_contract = Contract.objects.create(
        client=client,
        price=price,
        balance=price,
        signed=signed,
    )
    assign_perm('change_contract', new_contract.client.contact, new_contract)
    console.print("[green]Client successfully created.")
    table = create_table(new_contract)
    console.print(table)


@app.command()
def change(
    ctx: typer.Context,
    contract_id: Annotated[
        UUID,
        typer.Argument(
            help="Contract's id"
        )
    ],
    client: Annotated[
        bool,
        typer.Option(
            "--client",
            "-c",
            help="Change client"
        )
    ] = False,
    price: Annotated[
        bool,
        typer.Option(
            "--price",
            "-p",
            help="Change price",
            min=0
        )
    ] = False,
    balance: Annotated[
        bool,
        typer.Option(
            "--balance",
            "-b",
            help="Change balance",
            min=0
        )
    ] = False,
    signed: Annotated[
        bool,
        typer.Option(
            "--signed",
            "-s",
            help="Change signed status",
        )
    ] = False,
    all_fields: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Change all fields. It's same as -cpbs",
        )
    ] = False,
):
    """
    Update a contract.
    """
    try:
        contract = Contract.objects.get(id=contract_id)
    except ObjectDoesNotExist:
        console.print("[red]Client not found.")
        raise typer.Exit()

    if (
        user.groups.first().name != 'management'
        and not user.has_perm('change_contract', contract)
    ):
        console.print("[red]You are not allowed.")
        raise typer.Exit()

    fields_to_change = {}

    for key, value in ctx.params.items():
        if key in {"contract_id", "all_fields"}:
            continue
        if all_fields:
            value = True
        if key == "signed":
            fields_to_change[key] = typer.confirm('Contract signed ?')
        elif value:
            fields_to_change[key] = prompt_for(
                message=key,
                validator_name=key,
                ctx=ctx
            )

    if fields_to_change:
        for key, value in fields_to_change.items():
            if key == 'client':
                remove_perm(
                    'change_contract',
                    contract.client.contact,
                    contract
                )
                assign_perm('change_contract', value.contact, contract)
            setattr(contract, key, value)
        contract.save()

    table = create_table(contract)
    console.print(table)
