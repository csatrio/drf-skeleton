import sys
import inspect
from django.contrib import admin
from django.db.models.query_utils import DeferredAttribute


def get_class(_name):
    return [obj for name, obj in inspect.getmembers(sys.modules[_name], inspect.isclass)
            if obj.__module__ is _name]


def get_model_fields(_model):
    return tuple(field_name for field_name, _type in _model.__dict__.items() if
                 type(_type) == DeferredAttribute and 'id' not in field_name)


def auto_register_model_admin(classes):
    for model in classes:
        try:
            if not getattr(model, 'is_automatic'):
                continue
        except AttributeError:
            pass
        model_admin = type(f"{model.__name__}Admin", (admin.ModelAdmin,), {'list_display': get_model_fields(model)})
        admin.site.register(model, model_admin)
