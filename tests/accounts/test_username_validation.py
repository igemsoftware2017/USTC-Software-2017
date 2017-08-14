from unittest import TestCase

from biohub.accounts.validators import UsernameValidator, ValidationError


class Test(TestCase):

    def test_username(self):

        for username in ['a', 'a' * 21, 'aaaaaaa+']:
            with self.assertRaises(ValidationError):
                UsernameValidator()(username)

        for username in ['abcdef']:
            UsernameValidator()(username)
