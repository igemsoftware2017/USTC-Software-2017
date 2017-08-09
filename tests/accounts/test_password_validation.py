from unittest import TestCase

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class Test(TestCase):

    def test_validation(self):
        for password in ['ab12', 'aaaaaaaa', 'a' * 30, '1' * 7]:
            with self.assertRaises(ValidationError):
                validate_password(password)
