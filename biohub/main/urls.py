# from django.conf.urls import url
# from django.contrib import admin

from biohub.core.routes import urlpatterns as biohub_urlpatterns

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
] + biohub_urlpatterns
