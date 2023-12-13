from jwt.exceptions import ExpiredSignatureError
from unittest.mock import patch, PropertyMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from cli.utils.user import get_user
from cli.utils.token import TokenNotFoundError


User = get_user_model()


class TestGetUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            first_name='user',
            last_name='sales',
            email='user@sales.com',
            phone='0611111111',
            password='password',
            department=Group.objects.get(name='sales')
        )

    @patch(
        'cli.utils.token.Token.decode',
        new_callable=PropertyMock
    )
    def test_return_user(self, mock_token_decode):
        mock_token_decode.return_value = {
            'user_id': self.user.id
        }
        with patch('cli.utils.user.get_user') as mock:
            mock.return_value = self.user
            user = mock()
        self.assertIsInstance(user, User)
        self.assertEqual(user, self.user)

    @patch(
        'cli.utils.token.Token.decode',
        new_callable=PropertyMock,
        side_effect=ExpiredSignatureError
    )
    def test_token_expired(self, mock_token_decode):
        user = get_user()
        self.assertEqual(user, None)

    @patch(
        'cli.utils.token.Token.decode',
        new_callable=PropertyMock,
        side_effect=TokenNotFoundError
    )
    def test_token_not_found(self, mock_token_decode):
        user = get_user()
        self.assertEqual(user, None)

    @patch(
        'cli.utils.token.Token.decode',
        new_callable=PropertyMock,
        return_value={'user_id': 10}
    )
    def test_object_does_not_exist(self, mock_token_decode):
        user = get_user()
        self.assertEqual(user, None)
