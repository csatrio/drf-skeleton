from django.conf.urls import url, include
from rest_framework import routers
from .models import classes as model_classes
from common.components import generic_view
import os

router = routers.DefaultRouter()
dir_name = os.path.dirname(os.path.abspath(__file__)).replace(os.getcwd(), '').replace(os.sep, '').strip()

for model in model_classes:
    router.register(model.__name__.lower(), generic_view(model))

urlpatterns = [
    url(f"^{dir_name}/", include(router.urls)),
]
