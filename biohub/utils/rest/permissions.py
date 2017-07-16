from rest_framework.permissions import (  # noqa:F403
    BasePermission, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)  # noqa: F403
from rest_condition import C  # noqa:F403


def check_owner(field_name=None, methods=('PUT', 'PATCH')):
    """
    A factory function to create permission class to check whether a user
    'owns' an object. The user field of the object is specified by `field_name`
    (None for itself). An optional argument `methods` may be provided to
    indicate under what circumstances the check will occur.
    """

    class P(BasePermission):

        def has_object_permission(self, request, view, obj):

            if field_name is not None:
                assert hasattr(obj, field_name),\
                    'Cannot resolve %r into a field of %r.' % (
                        field_name, obj.__class__)
                user_to_check = getattr(obj, field_name)
            else:
                user_to_check = obj

            if request.method not in methods:
                return True

            user = request.user
            return user.is_authenticated() and user.pk == user_to_check.id

    return P
