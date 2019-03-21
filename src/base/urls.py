"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers
from common.components import generic_view
import importlib

API_PREFIX = 'api'
ADMIN_URL = 'api_admin'

router = routers.DefaultRouter()
secondary_urls = []

# auto append child application module
for module in settings.APP_MODULES:
    # append url in every app module
    try:
        models = importlib.import_module(f"{module}.models")
        secondary_router = routers.DefaultRouter()
        # crete view for each and every model
        for model in models.classes:
            view_class = generic_view(model)
            router.register(f"{module}/{model.__name__.lower()}", view_class)
            secondary_router.register(model.__name__.lower(), view_class)
        secondary_urls.append(url(f"^{API_PREFIX}/{module}/", include(secondary_router.urls)))
    except AttributeError:
        pass

    # append urls found in secondary url config
    try:
        urls = importlib.import_module(f"{module}.urls")
        try:
            for child_url in urls.urlpatterns:
                secondary_urls.append(child_url)
        except AttributeError:
            pass
    except ModuleNotFoundError:
        pass

urlpatterns = [
                  path(f"{ADMIN_URL}/", admin.site.urls),
                  url(f"^{API_PREFIX}/api-auth/", include('rest_framework.urls', namespace='rest_framework')),
                  url(f"^{API_PREFIX}/", include(router.urls))
              ] + secondary_urls
