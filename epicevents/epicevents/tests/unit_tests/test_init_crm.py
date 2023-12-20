import os
from dotenv import dotenv_values
from django.test import TestCase
from epicevents.init_crm import generate_secret_key


class TestInitCRM(TestCase):
    file_name = '.env.test'

    def test_generate_secret_key(self):
        if os.path.exists('.env.test'):
            os.remove('.env.test')
        secret = generate_secret_key(file_name=self.file_name)
        self.assertEqual(secret, os.environ.get('SECRET_KEY'))
        self.assertTrue(dotenv_values(self.file_name).get('SECRET_KEY'))
        self.assertTrue(os.path.exists('.env.test'))
