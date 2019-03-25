from .auto_views import *
from django.conf.urls import url, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register('test_perpus/Anggota', AnggotaViewSet)
router.register('test_perpus/Buku', BukuViewSet)
router.register('test_perpus/DetilSewa', DetilSewaViewSet)
router.register('test_perpus/Sewa', SewaViewSet)
urlpatterns = [url('test_perpus', include(router.urls)), ]
