from rich.table import Table


FIELDS = {
    'user': [
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'groups__name',
        'created',
        'updated',
    ],
    'client': [
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'compagny__name',
        'contact__first_name',
        'contact__last_name',
        'created',
        'updated',
    ],
    'contract': [
        'id',
        'client__first_name',
        'client__last_name',
        'client__contact__first_name',
        'client__contact__last_name',
        'price',
        'balance',
        'signed',
        'created',
        'updated',
    ],
    'event': [
        'id',
        'name',
        'start_date',
        'end_date',
        'location',
        'attendees',
        'contract',
        'contact__first_name',
        'contact__last_name',
        'note',
        'created',
        'updated',
    ]
}


def get_fields_name(fields):
    """Parse fields"""
    return [field.replace('__', ' ').replace('_', ' ') for field in fields]


def get_type(obj):
    """Get the type of the object as string"""
    return obj._meta.model.__name__


def get_model(obj):
    """Get the model of the object"""
    return obj._meta.model


def create_table(queryset_or_obj):
    """Create table.
    If queryset_or_obj is a signle object create
    a queryset with this object.

    args:
        queryset_or_obj : a single object or a queryset

    returns:
        a rich table object
    """
    try:
        obj = queryset_or_obj.first()
        queryset = queryset_or_obj
    except AttributeError:
        obj = queryset_or_obj
        queryset = get_model(obj).objects.filter(id=obj.id)
    if not obj:
        return Table()
    type_obj = get_type(obj)
    table = Table(title=type_obj + 's', header_style='blue')
    table = table_add_column(table, type_obj)
    table = table_add_row(table, type_obj, queryset)
    return table


def table_add_column(table, type_obj):
    """Create columns dynamically related to type_obj"""
    previous_field = None
    for field_name in FIELDS[type_obj.lower()]:
        if '__first_name' in field_name:
            previous_field = field_name
            continue
        elif field_name == 'groups__name':
            field_name = 'department'
        if previous_field:
            field_name = f"{field_name.split('__')[-2]} name"
            previous_field = None
        table.add_column(
            field_name.replace('__', ' ').replace('_', ' ').upper(),
            justify='center',
        )
    return table


def table_add_row(table, type_obj, queryset):
    """Create rows dynamically related to type_obj and queryset"""
    fields = FIELDS[type_obj.lower()]
    for values_tuple in queryset.values_list(*fields, named=True):
        values = []
        previous_value = None
        for key, value in values_tuple._asdict().items():
            if '__first_name' in key:
                previous_value = value
                continue
            if previous_value:
                value = f'{previous_value} {value}'
                previous_value = None
            values.append(str(value))
        table.add_row(*values)
    return table
