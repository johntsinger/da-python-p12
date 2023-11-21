from django.contrib.auth.models import Group
from django.conf import settings
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
        for codename in settings.PERMISSIONS[group.name]:
            assign_perm('orm.' + codename, group)
        for codename in settings.PERMISSIONS['all']:
            assign_perm('orm.' + codename, group)


def set_object_permissions(sender, **kwargs):
    pass