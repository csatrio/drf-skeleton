import os

from django.apps import AppConfig


class AppCommonConfig(AppConfig):
    name = os.path.dirname(os.path.abspath(__file__)).replace(os.getcwd(), '').replace(os.sep, '').strip()
