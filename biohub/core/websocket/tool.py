from channels import Group
from django.utils.lru_cache import lru_cache


@lru_cache(maxsize=None)
def get_group(name):
    """
    A shortcut to get and cache a Group object.
    """
    return Group(name)


def broadcast(data):
    """
    To make a global broadcasting.
    """
    return get_group('broadcast').send(data)


def broadcast_user(user, data):
    """
    To broadcast to specified user.
    """
    return get_group('user_%s' % user.id).send(data)


def broadcast_users(users, data):
    """
    To broadcast to specified users.
    """
    return [
        get_group('user_%s' % user.id).send(data)
        for user in users
    ]
