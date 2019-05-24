import inspect
import sys
from django.conf import settings
from django.contrib import admin
from django.db.models.query_utils import DeferredAttribute
import django.db.models.fields.related_descriptors as related_descriptors


def create_class(_name: str, _superclasses: tuple, _attributes: dict):
    _class = settings.CLASS_CACHE.get(_name)
    if _class is None:
        _class = type(_name, _superclasses, _attributes)
        settings.CLASS_CACHE[_name] = _class
    return _class


def get_cached_class(_name: str):
    return settings.CLASS_CACHE.get(_name)


def get_classes(_name):
    return [obj for name, obj in inspect.getmembers(sys.modules[_name], inspect.isclass)
            if obj.__module__ is _name]


def get_model_fields(_model):
    return tuple(field_name for field_name, _type in _model.__dict__.items() if
                 type(_type) == DeferredAttribute and 'id' not in field_name)


RELATED_FIELD_CLASS = get_classes(related_descriptors.__name__)


def register_model_admin(model):
    search_fields = []
    list_fields = []

    for field_name, _type in model.__dict__.items():
        if type(_type) == DeferredAttribute:
            if 'id' not in field_name: search_fields.append(field_name)
        elif type(_type) in RELATED_FIELD_CLASS:
            if '_set' not in field_name: list_fields.append(field_name)

    model_admin = type(f"{model.__name__}Admin", (admin.ModelAdmin,),
                       {'list_display': search_fields, 'list_filter': list_fields, 'search_fields': search_fields})
    admin.site.register(model, model_admin)
