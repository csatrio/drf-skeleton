from django.contrib import admin

from common.components import child_url_resolver
from .views import *

url = child_url_resolver(__file__)
urlpatterns = [
    url('admin/', admin.site.urls),
    url('ds/', get_sewa_detail)
]
