from pathlib import Path
from dotenv import load_dotenv
import os
from epicevents.init_crm import generate_secret_key


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load environment variables
load_dotenv()

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
    'cli.apps.CliConfig'
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
        'add_event',
    ],
    'support': []
}
