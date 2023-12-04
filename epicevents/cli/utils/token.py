import os
import jwt
from pathlib import Path
from dotenv import set_key


class TokenNotFoundError(Exception):
    pass


class BaseToken:
    TOKEN = 'TOKEN'
    KEY = 'SECRET_KEY'

    @staticmethod
    def create_env_file(content, path='', file_name='.env'):
        path = Path(path)
        if not Path.is_file(path / file_name):
            with open(path / file_name, 'w') as file:
                file.write(content)

    @classmethod
    def _get_secret_key(cls):
        return os.environ.get(cls.KEY)

    @classmethod
    def _save_token_to_env(cls, token, file_name='.env'):
        file_name = Path(file_name)
        if not Path.is_file(file_name):
            with open(file_name, 'w') as file:
                file.write(f'TOKEN={token}')
        else:
            os.environ[cls.TOKEN] = token
            set_key('.env', cls.TOKEN, token)

    @classmethod
    def _delete_token_from_env(cls):
        os.environ.pop(cls.TOKEN, None)

    @classmethod
    def _get_token_from_env(cls):
        return os.environ.get(cls.TOKEN)

    @classmethod
    def _decode_token(cls, token, key, raise_error=True):
        if raise_error:
            return jwt.decode(token, key, algorithms='HS256')
        try:
            return jwt.decode(token, key, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return None

    @classmethod
    def _token_is_valid(cls, token, key):
        try:
            cls._decode_token(token, key)
        except jwt.ExpiredSignatureError:
            return False
        return True

    @classmethod
    def _is_token_in_env(cls):
        token = cls._get_token_from_env()
        if token:
            return True
        return False


class NewToken(BaseToken):
    """Generate a new token when instanciated
    and save it to .env file
    """

    def __init__(self, payload):
        self._key = os.environ.get(self.KEY)
        self._payload = payload
        self._create_token()

    def _new_token(self):
        return jwt.encode(
            self._payload,
            self._key,
            algorithm="HS256"
        )

    def _is_user_token(self, token):
        payload = self._decode_token(token, self._key, raise_error=False)
        if not payload:
            return False
        if (
            (payload['user_id'], payload['sub'])
            == (self._payload['user_id'], self._payload['sub'])
        ):
            return True
        return False

    def _create_token(self):
        if self._is_token_in_env():
            token = self._get_token_from_env()
            if (
                self._token_is_valid(token, self._key)
                and self._is_user_token(token)
            ):
                return None
            else:
                self._delete_token_from_env()
        token = self._new_token()
        self._save_token_to_env(token)


class Token(BaseToken):
    """Get the current saved token"""

    def __init__(self):
        self.token = self._get_token_from_env()
        if not self.token:
            raise TokenNotFoundError()

    @property
    def decode(self):
        """Decode token and return payload as dict"""
        key = os.environ.get(self.KEY)
        if self._token_is_valid(self.token, key):
            return self._decode_token(self.token, key)
        raise jwt.ExpiredSignatureError()
