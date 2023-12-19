from unittest.mock import patch
from django.test import TestCase
from cli.utils.prompt import prompt_for


class Obj:
    def __init__(self):
        self.phone = '+33600000000'


class Context:
    def __init__(self):
        self.obj = Obj()


class TestPromptFor(TestCase):
    ctx = Context()

    @patch('typer.prompt', return_value='0600000000')
    def test_prompt_for(self, mock_typer_prompt):
        value = prompt_for('phone', self.ctx)
        self.assertEqual(value, '+33600000000')
