from django.core.signing import Signer, BadSignature
from django.utils.crypto import get_random_string

signer = Signer(salt='Salt for abacus.')


def signature():
    """
    Generates a random signature.
    """
    return signer.sign(get_random_string())


def validate_signature(signature):
    """
    Validates if the signature is correct.
    """
    try:
        signer.unsign(signature)
    except BadSignature:
        return False
    else:
        return True
