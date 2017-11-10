import base64
from functools import wraps

from django.http import HttpResponse
from django.core.signing import Signer


class basicauth:

    def __init__(self, realm, password):
        self.realm = realm
        self.password = password

    def __call__(self, view):

        @wraps(view)
        def wrapper(request, *args, **kwargs):

            if 'HTTP_AUTHORIZATION' in request.META:
                auth_info = request.META['HTTP_AUTHORIZATION'].split()

                if len(auth_info) == 2 and auth_info[0].lower() == 'basic':
                    password = base64.b64decode(auth_info[1]).decode().split(':')[1]

                    if ':'.join((self.password, password)) == Signer().sign(self.password):
                        return view(request, *args, **kwargs)

            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm=%s' % self.realm

            return response
        return wrapper

def get_ip_from_request(request):
    """
    An intelligent method to get real IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
