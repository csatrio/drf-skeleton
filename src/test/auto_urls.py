from .auto_views import *
from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('test/Person', PersonViewSet)
urlpatterns = [url('test', include(router.urls)), ]
