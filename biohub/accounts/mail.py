from django.core import mail


def get_password_reset_email(user, callback, connection=None):
    email = mail.EmailMessage(
        'Biohub Password Reset',
        (
            'Click here to reset: <a href="{callback}" target="_blank">{callback}</a>.'
        ).format(callback=callback),
        to=[user.email],
        connection=connection
    )
    email.content_subtype = 'html'
    return email
