from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from biohub.forum.models import Article

        for article in Article.objects.all():
            if not article.digest:
                article.make_digest()
                article.save()
