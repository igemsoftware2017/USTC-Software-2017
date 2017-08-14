from rest_framework.authentication import SessionAuthentication


class NoCSRFAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return
