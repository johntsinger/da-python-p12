import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epicevents.settings')
django.setup()


if __name__ == '__main__':
    from cli.commands.cli import app
    app()
