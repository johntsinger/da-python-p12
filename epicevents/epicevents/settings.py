from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'de@n)4-y$0kj#bq4aww^ad$py9@@a^n@wjv_@*1x95(sythg8q'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_extensions',
    'guardian',
    'orm.apps.OrmConfig'
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_USER_MODEL = 'orm.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

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
