import re

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
        is_valid = re.search(r'^\w{6,20}$', password) \
            and re.search(r'\d', password) and re.search(r'[a-zA-Z]', password)

        if not is_valid:
            raise ValidationError(
                "Password should contain both numbers and English letters, "
                "with the length no less than 6 and no more than 20.")
