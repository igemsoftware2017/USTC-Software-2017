import re
import string

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class UsernameValidator(validators.RegexValidator):

    regex = r'^[\da-zA-Z_]{4,15}$'
    message = (
        'Enter a valid username. This value may contain only English letters, '
        'numbers and underscores, with the length no less than 4 and no less '
        'than 15.')
    flags = re.ASCII


class PasswordValidator(object):

    def validate(self, password, user=None):
        digits_and_letters = frozenset(string.digits + string.ascii_letters)

        is_valid = set(password) & digits_and_letters
        is_valid = is_valid and re.search(r'^\w{6,20}$', password)

        if not is_valid:
            raise ValidationError(
                "Password should contain both numbers and English letters, "
                "with the length no less than 6 and no more than 20.")
