import os
import sys
import inspect
from django.contrib import admin
from django.db.models.query_utils import DeferredAttribute
from django.conf import settings

out_file_name = os.path.join(os.getcwd(), 'common', 'auto_serializer_filter.py')
print(out_file_name)
try:
    os.remove(out_file_name)
except FileNotFoundError:
    pass

TAB = '\t'
NEWLINE = '\n'
NEWLINE_TAB = '\n\t'


class ClassDumper(object):
    disallowed_attributes = ['__', '_declared_fields', 'declared_filters', 'validators']
    allowed_attributes = ['model', 'serializer', 'pagination_class']

    def __init__(self, module_name: str):
        self.module_name = module_name

        self.serializer_filter = open(os.path.join(os.getcwd(), module_name, 'auto_serializer_filter.py'), 'w+')
        self.serializer_filter.writelines(
            'from .models import *\n'
            'from common.components import BaseDjangoFilter, BaseSerializer\n'
            '\n\n'
        )
        self.views = open(os.path.join(os.getcwd(), module_name, 'auto_views.py'), 'w+')
        self.views.writelines(
            'from .auto_serializer_filter import *\n'
            'from common.components import BaseView, Pager\n'
            '\n\n'
        )
        self.admin = open(os.path.join(os.getcwd(), module_name, 'auto_admin.py'), 'w+')
        self.admin.writelines(
            'from django.contrib import admin\n\n'
        )
        self.urls = open(os.path.join(os.getcwd(), module_name, 'auto_urls.py'), 'w+')
        self.urls.writelines(
            'from .auto_views import *\n'
            'from django.conf.urls import url, include\n'
            'from rest_framework import routers\n\n'
            'router = routers.DefaultRouter()\n'
        )

    def close(self):
        self.serializer_filter.close()
        self.views.close()
        self.admin.close()
        self.urls.writelines(f"urlpatterns = [url('{self.module_name}', include(router.urls)), ]\n")
        self.urls.close()

    def process_class_items(self, k, v, rq=None, _model=None):
        key = str(k)
        if 'Meta' in key:
            key = ''
            value = self.attr_to_meta(v.__dict__)
        else:
            key += ' = '
            if v == tuple or v == dict:
                value = str(v)
            elif self.chk_attr(key, attribute_list=self.allowed_attributes, allowed=True):
                value = v.__name__
            elif 'filter_backends' in key:
                value = f"({v[0].__name__},)"
            elif 'queryset' in key:
                if rq is not None and len(rq) > 0:
                    values = ["'" + q + "'" for q in rq]
                    value = f"{_model.__name__}.objects.all(){ '.select_related(' + ', '.join(values) +')' }"
                else:
                    value = f"{_model.__name__}.objects.all()"
            else:
                value = str(v)

        return f"{TAB}{key}{value}"

    @staticmethod
    def chk_attr(k, attribute_list=disallowed_attributes, allowed=False):
        for item in attribute_list:
            if item in k:
                return False if not allowed else True
        return True if not allowed else False

    def attr_to_meta(self, attributes: dict):
        attrs = [self.process_class_items(k, v) for k, v in attributes.items() if ClassDumper.chk_attr(k)]
        return f"class Meta:\n\t" \
               f"{NEWLINE_TAB.join(attrs)}\n"

    def class_to_text(self, _class: str, _superclasses: tuple, attributes: dict, rq=None, _model=None):
        attrs = [self.process_class_items(k, v, rq, _model) for k, v in attributes.items() if ClassDumper.chk_attr(k)]
        cls = f"class {_class}({','.join([sc.__name__  for sc in _superclasses])}):\n" \
              f"{NEWLINE.join(attrs)}\n\n\n"
        print(_class)

        if 'Serializer' in _class or 'Filter' in _class:
            self.serializer_filter.write(cls)
            self.serializer_filter.flush()

        if 'ViewSet' in _class:
            self.views.writelines(cls)
            self.views.flush()

            self.urls.writelines(f"router.register('{self.module_name}/{_model.__name__}', {_class})\n")
            self.urls.flush()


class KeyedClassDumper(dict):
    def dump(self, _class: str, _superclasses: tuple, attributes: dict, rq=None, _model=None, module=None):
        _dumper = self.get(module)
        if not _dumper:
            _dumper = ClassDumper(module)
            self[module] = _dumper
        _dumper.class_to_text(_class, _superclasses, attributes, rq=rq, _model=_model)

    def close(self):
        for item in self.values():
            item.close()
        self.clear()


dumper = KeyedClassDumper()


def create_class(_name: str, _superclasses: tuple, _attributes: dict, rq=None, _model=None, module_name=None):
    _class = settings.CLASS_CACHE.get(_name)
    if _class is None:
        _class = type(_name, _superclasses, _attributes)
        if 'Meta' not in _name:
            dumper.dump(_name, _superclasses, _attributes, rq=rq, _model=_model, module=module_name)
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
