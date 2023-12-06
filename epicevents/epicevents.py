import os
import django
from sentry_sdk import capture_exception, set_context


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epicevents.settings')
django.setup()


if __name__ == '__main__':
    from cli.commands.cli import app
    from cli.utils.user import get_user
    user = get_user()
    set_context(
        "user", {
            "id": user.id,
            "name": user.get_full_name(),
            "department": user.groups.first().name
        }
    )
    # run the app and capture any exceptions to send to sentry
    try:
        app()
    except Exception as e:
        capture_exception(e)
