"""
This module provides shortcuts for notice dispatching.

Instead of generating notice message by concatenate strings, you can now use
django template syntax to render it. The class `Dispatcher` defines an
interface of category-specific notice dispatching.

Note that `notices.tool` has a special filter `url` to generate link tag.
`{{ 'text' | url: 'url' }}` will be interpreted into `[[text]]((url))`, which
may be further transformed into `<a>` tag by javascript. The design provides
you more flexibility.
"""

from django.template import engines

from .models import Notice

__all__ = ['Dispatcher']


def render_notice_message(template, dispatcher, **context):

    engine = engines['notices']
    return engine.from_string(template).render(dict(
        category=dispatcher.category,
        **context))


class Dispatcher(object):

    def __init__(self, category):
        """
        Notices dispatched from this dispatcher will automatically have
        `category` as its category property.
        """
        self.__category = category

    @property
    def category(self):
        return self.__category

    def send(self, user, template, **context):
        """
        Send a notice to user.
        `user`, `category` and `context` will all be applied as template
        context.
        """

        message = render_notice_message(
            template, self, user=user, **context)

        return Notice.objects.create(
            user=user,
            message=message,
            category=self.category
        )

    def group_send(self, users, template, **context):
        """
        Send a notice to each user in `users`. Note that for performance
        consideration, this method uses `bulk_create`.
        Template context will be served the same as `send` do.
        """

        results = []

        for user in users:
            message = render_notice_message(
                template, self, user=user, **context)

            results.append(
                Notice(
                    user=user,
                    message=message,
                    category=self.category))

        return Notice.objects.bulk_create(results)
