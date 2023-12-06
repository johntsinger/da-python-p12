import os
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set Sentry DNS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--set-dns",
            action="store_true",
            help='Set DNS for Sentry'
        )

    def handle(self, *args, **options):
        try:
            dns = options['set-dns']
        except KeyError:
            dns = input('DNS : ')

        file_name = Path(".dns.env")
        if not Path.is_file(file_name):
            with open(file_name, 'w') as file:
                file.write(
                    f"DNS={dns}"
                )
        print('DNS successfully added.')
