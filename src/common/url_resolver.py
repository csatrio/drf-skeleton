import os

from django.conf.urls import url as _url


def child_url_resolver(_file):
    current_folder = os.path.dirname(os.path.abspath(_file)).replace(os.getcwd(), '').replace(os.sep, '').strip()

    def url(*args):
        return _url(f"{current_folder}/{args[0]}", args[1])

    return url