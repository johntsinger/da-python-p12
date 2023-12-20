import os
from pathlib import Path
from dotenv import set_key, dotenv_values
from django.core.management.utils import get_random_secret_key


def generate_secret_key(base_dir='', file_name='.env'):
    base_dir = Path(base_dir)
    if not Path.is_file(base_dir / file_name):
        with open(base_dir / file_name, 'w'):
            pass
    values = dotenv_values(base_dir / file_name)
    if not values.get('SECRET_KEY'):
        key = get_random_secret_key()
        set_key(file_name, 'SECRET_KEY', key)
        os.environ['SECRET_KEY'] = key
        return key
