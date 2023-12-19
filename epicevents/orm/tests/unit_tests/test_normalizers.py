from django.test import TestCase
from orm.normalizers import normalize_email, normalize_phone


class TestNormalizers(TestCase):
    phone = '0600000000'
    phone_expected = '+33600000000'
    email = 'test@TEST.com'
    wrong_email = 'test'
    email_expected = 'test@test.com'

    def test_normalize_phone(self):
        phone = normalize_phone(self.phone)
        self.assertEqual(phone, self.phone_expected)

    def test_normalize_email(self):
        email = normalize_email(self.email)
        self.assertEqual(email, self.email_expected)

    def test_normalize_email_value_error(self):
        email = normalize_email(self.wrong_email)
        self.assertEqual(email, self.wrong_email)
