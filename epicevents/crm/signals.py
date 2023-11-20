from django.contrib.auth.models import Group
from epicevents.permissions import PERMISSIONS
from guardian.shortcuts import assign_perm


def create_department_group(sender, **kwargs):
    for department_name in [
        'management',
        'sales',
        'support'
    ]:
        if not Group.objects.filter(
            name=department_name
        ).exists():
            Group.objects.create(
                name=department_name
            )


def set_base_permissions(sender, **kwargs):
    groups = Group.objects.all()
    for group in groups:
        for codename in PERMISSIONS[group.name]:
            assign_perm('crm.' + codename, group)
        for codename in PERMISSIONS['all']:
            assign_perm('crm.' + codename, group)


def set_object_permissions(sender, **kwargs):
    pass