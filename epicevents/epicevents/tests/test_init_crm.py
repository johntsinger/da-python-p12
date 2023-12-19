from pathlib import Path
from unittest.mock import patch, mock_open
from django.test import TestCase
from epicevents.init_crm import generate_secret_key


class TestInitCRM(TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_secret_key(self, mock):
        generate_secret_key(file_name='.env.test.test')
        mock.assert_called_with(Path('.env.test.test'), 'w')
