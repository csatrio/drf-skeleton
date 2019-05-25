import inspect
import sys
import django.db.models.fields.related_descriptors as related_descriptors
from django.conf import settings
from django.contrib import admin
from django import forms
from django.db.models.query_utils import DeferredAttribute
from test_perpus.models import *


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


class CustomForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'sewa' and hasattr(field, 'queryset'):
                for field_name, _type in field.queryset.model.__dict__.items():
                    if type(_type) in RELATED_FIELD_CLASS:
                        if '_set' not in field_name:
                            field.queryset = field.queryset.select_related(field_name)


class CustomAdmin(admin.ModelAdmin):
    isOptimizePrefetch = False
    form = CustomForm

    def get_queryset(self, request):
        qs = super(CustomAdmin, self).get_queryset(request)
        qs = qs.select_related(*self.related_fields)
        return qs


def lookup_related_field(model, model_name, related_fields):
    for field_name, _type in model.__dict__.items():
        if type(_type) in RELATED_FIELD_CLASS:
            if '_set' not in field_name:
                field = model._meta.get_field(field_name)
                related_field_name = f"{model_name}__{field_name}"
                related_fields.add(related_field_name)
                related_model = field.related_model
                lookup_related_field(related_model, related_field_name, related_fields)


def register_model_admin(model):
    search_fields = []
    list_fields = []
    related_fields = set()

    for field_name, _type in model.__dict__.items():
        if type(_type) == DeferredAttribute:
            if 'id' not in field_name: search_fields.append(field_name)
        elif type(_type) in RELATED_FIELD_CLASS:
            if '_set' not in field_name:
                list_fields.append(field_name)
                field = model._meta.get_field(field_name)
                related_fields.add(field_name)
                related_model = field.related_model
                lookup_related_field(related_model, field_name, related_fields)

    display_fields = search_fields + list_fields
    model_admin = type(f"{model.__name__}Admin", (CustomAdmin,),
                       {'list_display': display_fields,
                        'list_filter': list_fields,
                        'list_select_related': tuple(related_fields),
                        'search_fields': search_fields,
                        'related_fields': related_fields,
                        })
    admin.site.register(model, model_admin)
