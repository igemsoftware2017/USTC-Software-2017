from biohub.core.routes import register_default, url
from .views import upload

register_default(r'^files/', [
    url(r'^upload/$', upload, name='upload')
], namespace='files')
