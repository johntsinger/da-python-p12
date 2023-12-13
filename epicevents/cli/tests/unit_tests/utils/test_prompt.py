from unittest.mock import patch
from django.test import TestCase
from cli.utils.prompt import prompt_for


class TestPromptFor(TestCase):
    @patch('typer.prompt', return_value='0600000000')
    def test_prompt_for(self, mock_typer_prompt):
        value = prompt_for('test', validator_name='phone')
        self.assertEqual(value, '+33600000000')
