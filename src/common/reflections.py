import os
import sys
import inspect
from django.contrib import admin
from django.db.models.query_utils import DeferredAttribute
from django.conf import settings

out_file_name = '/home/csatrio/Desktop/xx.py'
try:
    os.remove(out_file_name)
except FileNotFoundError:
    pass

newline = '\n'
newline_tab = '\n\t'

disallowed_attributes = ['__', '_declared_fields', 'declared_filters', 'validators']
allowed_attributes = ['model', 'serializer', 'pagination_class']


def process_class_items(k, v, rq=None, _model=None):
    key = str(k)
    if 'Meta' in key:
        key = ''
        value = attr_to_meta(v.__dict__)
    else:
        key += '='
        if v == tuple or v == dict:
            value = str(v)
        elif chk_attr(key, attribute_list=allowed_attributes, allowed=True):
            value = v.__name__
        elif 'filter_backends' in key:
            value = v[0].__name__
        elif 'queryset' in key:
            if rq is not None and len(rq) > 0:
                values = ["'" + q + "'" for q in rq]
                value = f"{_model.__name__}.objects.all(){ '.select_related(' + ','.join(values) +')' }"
            else:
                value = f"{_model.__name__}.objects.all()"
        else:
            value = str(v)

    return '\t' + key + value


def chk_attr(k, attribute_list=disallowed_attributes, allowed=False):
    for item in attribute_list:
        if item in k:
            return False if not allowed else True
    return True if not allowed else False


def attr_to_meta(attributes: dict):
    return f"class Meta:\n\t" \
           f"{newline_tab.join([process_class_items(k,v) for k,v in attributes.items() if chk_attr(k)])}\n\n"


def class_to_text(_class: str, _superclasses: tuple, attributes: dict, rq=None, _model=None):
    return f"class {_class}({','.join([sc.__name__  for sc in _superclasses])}):\n" \
           f"{newline.join([process_class_items(k,v,rq,_model) for k,v in attributes.items() if chk_attr(k)])}\n\n"


def create_class(_name: str, _superclasses: tuple, _attributes: dict, rq=None, _model=None):
    _class = settings.CLASS_CACHE.get(_name)
    if _class is None:
        _class = type(_name, _superclasses, _attributes)
        if 'Meta' not in _name:
            with open(out_file_name, 'a') as out_file:
                data = class_to_text(_name, _superclasses, _attributes, rq, _model)
                out_file.writelines(data)
                out_file.flush()
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


def auto_register_model_admin(classes):
    for model in classes:
        try:
            if not getattr(model, 'is_automatic'):
                continue
        except AttributeError:
            pass
        model_admin = type(f"{model.__name__}Admin", (admin.ModelAdmin,), {'list_display': get_model_fields(model)})
        admin.site.register(model, model_admin)
