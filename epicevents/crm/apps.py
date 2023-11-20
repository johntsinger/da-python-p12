from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'

    def ready(self):
        from crm.signals import (
            create_department_group,
            set_base_permissions
        )
        post_migrate.connect(create_department_group, sender=self)
        post_migrate.connect(set_base_permissions, sender=self)
