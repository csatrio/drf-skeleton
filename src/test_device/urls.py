from django.contrib import admin

from common.url_resolver import child_url_resolver

url = child_url_resolver(__file__)

urlpatterns = [
    url('admin/', admin.site.urls)
]
