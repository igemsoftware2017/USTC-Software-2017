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
from django.db.models.functions import Now
from django.contrib.contenttypes.models import ContentType

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

    def _get_notice_instance(self, user, template, context, save=False):

        message = render_notice_message(
            template, self, user=user, **context)

        constructor = Notice.objects.create if save else Notice

        return constructor(
            user=user,
            message=message,
            category=self.category,
            target=context.get('target', None),
            target_slug=context.get('target_slug', ''),
            actor=context.get('actor', None)
        )

    def send(self, user, template, **context):
        """
        Send a notice to user.
        `user`, `category` and `context` will all be applied as template
        context.
        """

        return self._get_notice_instance(user, template, context, save=True)

    def send_or_update(self, user, template, **context):
        """
        Update or send a notice.
        The notices to update are located by `target`, `target_slug`, `actor`,
        which are ALL required to be specified.
        """

        filter_fields = set(context.get('filter_fields', {'target', 'target_slug', 'actor', 'user', 'category'}))
        assert filter_fields, '`filter_fields` should not be empty.'

        specified = {'user', 'category', *context}
        missing = filter_fields - specified
        assert not missing, 'Members %s of `filter_fields` are missing.' % ', '.join(missing)

        keywords = {
            name: value
            for name, value in {
                'user': user, 'template': template, 'category': self.category,
                **context
            }.items()
            if name in filter_fields
        }

        if 'target' in filter_fields and context['target'] is not None:
            target = context['target']
            ctype = ContentType.objects.get_for_model(target)
            keywords.pop('target')
            keywords.update({
                'target_type': ctype,
                'target_id': target.pk
            })

        try_find = Notice.objects.filter(**keywords)

        if try_find.count():
            message = render_notice_message(
                template, self, user=user, **context)
            try_find.update(message=message, has_read=False, created=Now())
        else:
            return self.send(user, template, **context)

    def group_send(self, users, template, **context):
        """
        Send a notice to each user in `users`. Note that for performance
        consideration, this method uses `bulk_create`.
        Template context will be served the same as `send` do.
        """

        results = []

        for user in users:
            results.append(
                self._get_notice_instance(
                    user,
                    template,
                    context,
                    save=False
                )
            )

        return Notice.objects.bulk_create(results)
