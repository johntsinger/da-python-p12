import sys
from pathlib import Path
from dotenv import set_key
from sentry_sdk.utils import Dsn, BadDsn
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set Sentry DSN"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dsn",
            action="store",
            help="Set DSN for Sentry"
        )

    def handle(self, *args, **options):
        if options["dsn"]:
            dsn = options["dsn"]
        else:
            try:
                dsn = input("DSN : ")
            except KeyboardInterrupt:
                self.stderr.write("\nOperation cancelled.")
                sys.exit(1)

        try:
            Dsn(dsn)
        except BadDsn as err:
            self.stderr.write(f"{err}.")
            sys.exit(1)

        file_name = Path(".env")
        if not Path.is_file(file_name):
            with open(file_name, "w"):
                pass
        set_key(file_name, "DSN", dsn)
        self.stdout.write("DSN successfully added.")
