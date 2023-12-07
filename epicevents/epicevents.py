import os
import django
import sentry_sdk


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epicevents.settings')
django.setup()


if __name__ == '__main__':
    from cli.commands.cli import app
    # run the app and capture any exceptions to send to sentry
    try:
        app()
    except Exception as e:
        sentry_sdk.capture_exception(e)
    finally:
        sentry_sdk.flush()
