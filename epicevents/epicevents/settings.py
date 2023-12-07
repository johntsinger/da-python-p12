from pathlib import Path
from dotenv import load_dotenv
import os
from epicevents.init_crm import generate_secret_key
import sentry_sdk


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load environment variables
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR / '.dns.env')

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    generate_secret_key(BASE_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_extensions',
    'guardian',
    'orm.apps.OrmConfig',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_USER_MODEL = 'orm.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Guardian anonymous user
ANONYMOUS_USER_NAME = None

PERMISSIONS = {
    'all': [
        'view_client',
        'view_contract',
        'view_event',
        'view_user'
    ],
    'management': [
        'add_user',
        'change_user',
        'delete_user',
        'add_contract',
        'change_contract',
        'change_event',
    ],
    'sales': [
        'add_client',
        'change_client',
        'change_contract',
        'add_event',
    ],
    'support': [
        'change_event'
    ]
}

# Sentry ingore errors
ignore_errors = [KeyboardInterrupt]

# Sentry init

sentry_sdk.init(
    dsn=os.environ.get('DNS'),
    ignore_errors=ignore_errors,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
