from .auto_views import *
from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('test_device/Device', DeviceViewSet)
router.register('test_device/DeviceReport', DeviceReportViewSet)
router.register('test_device/Vendor', VendorViewSet)
urlpatterns = [url('test_device', include(router.urls)), ]
