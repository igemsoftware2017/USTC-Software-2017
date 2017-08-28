from functools import partial

from django.core.signing import dumps
from django.utils.crypto import get_random_string

sign = partial(dumps, salt='Salt for abacus.', compress=True)


def signature():
    """
    Generates a random signature.
    """
    return sign(get_random_string())


def validate_signature(async_result, signature):
    """
    Validates if the signature is correct.
    """
    return async_result.signature == signature
