import os
import jwt
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from django.test import TestCase
from cli.utils.token import BaseToken, NewToken, Token, TokenNotFoundError


class TestBaseToken(TestCase):
    key = 'secret'
    invalid_key = 'invalid'
    token = jwt.encode(
        {
            'test': 1
        },
        key,
        'HS256'
    )
    invalid_token = 'token'
    expired_token = jwt.encode(
        {
            'test': 1,
            'exp': datetime.now(tz=timezone.utc) - timedelta(hours=12)
        },
        key,
        'HS256'
    )

    def test_create_env_file(self):
        if os.path.exists('.env.test'):
            try:
                os.remove('.env.test')
            except PermissionError:
                time.sleep(0.1)
                os.remove('.env.test')
        content = ''
        BaseToken.create_env_file(content, file_name='.env.test')
        self.assertTrue(os.path.exists('.env.test'))

    @patch(
        'os.environ.get',
        return_value='secret',
        clear=True
    )
    def test_get_secret_key(self, mock_os_environ):
        secret = BaseToken._get_secret_key()
        self.assertEqual(secret, 'secret')

    @patch(
        'os.environ.get',
        return_value='token',
        clear=True
    )
    def test_save_token_to_existing_env(self, mock_os_environ):
        BaseToken._save_token_to_env('token', file_name='.env.test')
        self.assertEqual(
            mock_os_environ.return_value,
            'token'
        )

    @patch(
        'os.environ.get',
        return_value='token',
        clear=True
    )
    def test_save_token_to_unexisting_env(
        self,
        mock_os_environ,
    ):
        if os.path.exists('.env.test.test'):
            os.remove('.env.test.test')
        BaseToken._save_token_to_env('token', file_name='.env.test.test')
        self.assertEqual(
            mock_os_environ.return_value,
            'token'
        )
        os.remove('.env.test.test')

    def test_delete_token_from_env(self):
        BaseToken._delete_token_from_env()
        self.assertIsNone(os.environ.get('TOKEN'))

    def test_get_token_from_env(self):
        BaseToken._save_token_to_env('token', file_name='.env.test')
        token = BaseToken._get_token_from_env()
        self.assertIsNotNone(token)

    def test_decode_token(self):
        token = BaseToken._decode_token(self.token, self.key)
        self.assertEqual(token, {'test': 1})

    def test_decode_token_invalid_token_raising_decode_error(self):
        self.assertRaises(
            jwt.DecodeError,
            BaseToken._decode_token,
            token=self.invalid_token,
            key=self.key
        )

    def test_decode_token_expired_token_raising_expired_signature_error(self):
        self.assertRaises(
            jwt.ExpiredSignatureError,
            BaseToken._decode_token,
            token=self.expired_token,
            key=self.key
        )

    def test_decode_token_invalid_key_raising_invalid_signature_error(self):
        self.assertRaises(
            jwt.InvalidSignatureError,
            BaseToken._decode_token,
            token=self.token,
            key=self.invalid_key
        )

    def test_decode_token_invalid_token_not_raising_errors(self):
        token = BaseToken._decode_token(
            self.invalid_token,
            self.key,
            raise_error=False
        )
        self.assertIsNone(token)

    def test_decode_token_expired_token_not_raising_errors(self):
        token = BaseToken._decode_token(
            self.expired_token,
            self.key,
            raise_error=False
        )
        self.assertIsNone(token)

    def test_decode_token_invalid_key_not_raising_errors(self):
        token = BaseToken._decode_token(
            self.token,
            self.invalid_key,
            raise_error=False
        )
        self.assertIsNone(token)

    def test_token_is_valid(self):
        is_valid = BaseToken._token_is_valid(self.token, self.key)
        self.assertEqual(is_valid, True)

    def test_token_is_valid_ivalid_token(self):
        is_valid = BaseToken._token_is_valid(self.invalid_token, self.key)
        self.assertEqual(is_valid, False)

    def test_token_is_valid_expired_token(self):
        is_valid = BaseToken._token_is_valid(self.expired_token, self.key)
        self.assertEqual(is_valid, False)

    def test_token_is_valid_ivalid_key(self):
        is_valid = BaseToken._token_is_valid(self.token, self.invalid_key)
        self.assertEqual(is_valid, False)

    def test_is_token_in_env(self):
        is_in_env = BaseToken._is_token_in_env()
        self.assertEqual(is_in_env, True)

    def test_is_token_in_env_not_in_env(self):
        BaseToken._delete_token_from_env()
        is_in_env = BaseToken._is_token_in_env()
        self.assertEqual(is_in_env, False)


class NewTokenForTest(NewToken):
    def __init__(self, payload, file_name='.env.test'):
        self._file_name = file_name
        self._key = os.environ.get(self.KEY)
        self._payload = payload


class TestNewToken(TestCase):
    key = 'secret'
    payload = {
        'user_id': 1,
        'sub': 'john doe'
    }
    new_token = NewToken(payload, testing=True)

    def test_generate_new_token(self):
        token = self.new_token._new_token()
        self.assertTrue(token)

    def test_is_user_token(self):
        token = self.new_token._new_token()
        is_user_token = self.new_token._is_user_token(token)
        self.assertEqual(is_user_token, True)

    def test_is_user_token_invalid_token(self):
        invalid_token = 'invalid_token'
        is_user_token = self.new_token._is_user_token(invalid_token)
        self.assertEqual(is_user_token, False)

    def test_is_user_token_not_user_token(self):
        token = self.new_token._new_token()
        payload = {
            'user_id': 2,
            'sub': 'not user'
        }
        new_token = NewToken(payload, testing=True)
        is_user_token = new_token._is_user_token(token)
        self.assertEqual(is_user_token, False)

    def test_create_token(self):
        self.new_token._create_token()
        self.assertTrue(os.environ.get('TOKEN', None))

    def test_create_token_existing_invalid_token(self):
        payload = {
            'user_id': 1,
            'sub': 'john doe',
            'exp': datetime.now(tz=timezone.utc) - timedelta(hours=12)
        }
        new_token = NewToken(payload, testing=True)
        token = new_token._create_token()
        self.assertIsNone(token)

    def test_class_new_token(self):
        NewToken(self.payload, testing=True)
        self.assertTrue(os.environ.get('TOKEN', None))


class TestToken(TestCase):
    @patch('cli.utils.token.BaseToken._is_token_in_env', return_value=False)
    def test_decode_token_valid(self, mock):
        payload = {
            'user_id': 1,
            'sub': 'john doe',
            'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=30)
        }
        NewToken(payload, testing=True)
        token = Token()
        payload = token.decode
        self.assertIsInstance(payload, dict)
        self.assertEqual(list(payload.keys()), ['user_id', 'sub', 'exp'])

    @patch('cli.utils.token.BaseToken._is_token_in_env', return_value=False)
    def test_decode_token_invalid(self, mock):
        payload = {
            'user_id': 1,
            'sub': 'john doe',
            'exp': datetime.now(tz=timezone.utc) - timedelta(seconds=30)
        }
        NewToken(payload, testing=True)
        token = Token()
        with self.assertRaises(jwt.ExpiredSignatureError):
            token.decode

    def test_decode_token_no_token_in_env(self):
        os.environ.pop('TOKEN')
        self.assertRaises(
            TokenNotFoundError,
            Token,
        )
