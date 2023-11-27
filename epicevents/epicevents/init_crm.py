from pathlib import Path
from django.core.management.utils import get_random_secret_key


def generate_secret_key(base_dir='', file_name='.env'):
    base_dir = Path(base_dir)
    if not Path.is_file(base_dir / file_name):
        with open(base_dir / file_name, 'w') as file:
            secret_key = get_random_secret_key()
            file.write(
                f"SECRET_KEY={secret_key}"
            )
