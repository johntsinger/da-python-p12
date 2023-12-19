import sys
from pathlib import Path
from dotenv import set_key
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set secret key"

    def add_arguments(self, parser):
        parser.add_argument(
            "--key",
            action="store",
            help="Set secret key"
        )

    def handle(self, *args, **options):
        if options["key"]:
            secret_key = options["key"]
        else:
            try:
                secret_key = input("Secret key : ")
            except KeyboardInterrupt:
                self.stderr.write("\nOperation cancelled.")
                sys.exit(1)

        file_name = Path(".env")
        if not Path.is_file(file_name):
            with open(file_name, "w"):
                pass
        set_key(file_name, "SECRET_KEY", secret_key)
        self.stdout.write("Secret key successfully added.")
