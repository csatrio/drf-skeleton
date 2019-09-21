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
import importlib

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

import common.jwt as jwt
import common.reflections as reflections
from common.components import generic_view

API_PREFIX = settings.API_PREFIX
ADMIN_URL = settings.ADMIN_URL

router = routers.DefaultRouter()
secondary_urls = []

# auto append child application module
for module in settings.APP_MODULES:
    # append url in every app module
    try:
        models = importlib.import_module(f"{module}.models")
        model_classes = reflections.get_classes(models.__name__)
        secondary_router = routers.DefaultRouter()
        # create view for each and every model
        for model in model_classes:
            try:
                if not getattr(model, 'is_automatic'):
                    continue
            except AttributeError:
                pass
            optimize_select_related = True if not hasattr(model, 'optimize_select_related') else model.optimize_select_related
            view_class = generic_view(model, optimize_select_related=optimize_select_related)
            router.register(f"{module}/{model.__name__.lower()}", view_class)
            secondary_router.register(model.__name__.lower(), view_class)
            # create admin entry for each model
            reflections.register_model_admin(model, model_classes=model_classes, optimize_select_related=optimize_select_related)
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
                  path(f"{API_PREFIX}/token/", jwt.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path(f"{API_PREFIX}/token/refresh/", jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
                  url(f"^{API_PREFIX}/api-auth/", include('rest_framework.urls', namespace='rest_framework')),
                  url(f"^{API_PREFIX}/", include(router.urls))
              ] + secondary_urls
