from biohub.core.routes import register_api, register_default, url  # noqa

from .views import analyze_reverse, analyze

register_api(r'^biomap/', [
    url(r'(?P<part_name>BBa_\w+)/analyze/', analyze),
    url(r'(?P<part_name>BBa_\w+)/analyze_reverse/', analyze_reverse),
], 'biomap')
