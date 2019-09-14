import django.db.models.fields.related_descriptors as related_descriptors
import django.db.models.fields.files as file_fields
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CharField, ForeignKey, ManyToManyField
from django.db.models.query_utils import DeferredAttribute
from django_filters import CharFilter
from rest_framework import viewsets, generics, mixins, serializers
from rest_framework.utils.serializer_helpers import NestedBoundField, BoundField

import common.mixins as serializer_mixin
import common.reflections as reflections
from common.fields import BinaryTextField
from common.filters import BaseDjangoFilter
from common.pagination import Pager

RELATED_FIELD_CLASS = reflections.get_classes(related_descriptors.__name__)

filter_overrides = {
    BinaryTextField: {
        'filter_class': CharFilter
    }
}


class BaseView(viewsets.ModelViewSet, generics.ListAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    pass


class BaseSerializer(serializer_mixin.UniqueFieldsMixin, serializer_mixin.NestedCreateMixin,
                     serializer_mixin.NestedUpdateMixin):

    def __getitem__(self, key):
        field = self.fields[key]
        value = self.data.get(key)
        error = self.errors.get(key) if hasattr(self, '_errors') else None
        if isinstance(field, serializers.Serializer):
            return NestedBoundField(field, value, field.data)
        return BoundField(field, value, error)


def nested_serializer(_model, related_fields=None):
    serializer_class_name = f"{_model.__name__}Serializer"
    serializer_fields = []
    serializer_attributes = {}
    serializer_meta_attributes = {'model': _model, 'fields': serializer_fields, 'validators': []}

    for field_name, _type in _model.__dict__.items():
        type_class = type(_type)
        # if it is a primary key field
        # if field_name == 'id':
        #     continue

        # if it is a model field
        if type_class == DeferredAttribute:
            serializer_fields.append(field_name)

        # if it is a related field, create nested serializer
        elif type_class in RELATED_FIELD_CLASS:
            try:
                field = _model._meta.get_field(field_name)
                field_type = type(field)
                serializer_fields.append(field_name)
                related_model = field.related_model

                if field_type == ForeignKey:
                    if related_fields:
                        related_fields.add(f"{_model.__name__.lower()}__{field.name}")
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(
                        allow_null=True, read_only=True)
                if field_type == ManyToManyField:
                    if related_fields:
                        related_fields.add(f"{_model.__name__.lower()}__{field.name}")
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(many=True,
                                                                                                         read_only=True)
            except FieldDoesNotExist:
                pass

    serializer_meta_class = reflections.create_class(f"{_model.__name__}SerializerMeta", (type,),
                                                     serializer_meta_attributes)
    serializer_attributes['Meta'] = serializer_meta_class
    serializer_class = reflections.create_class(serializer_class_name, (BaseSerializer,),
                                                serializer_attributes)
    return serializer_class


def generic_view(_model):
    view_set_class_name = f"{_model.__name__}ViewSet"
    cached_class = reflections.get_cached_class(view_set_class_name)
    if cached_class:
        return cached_class

    text_column = []
    serializer_fields = []
    filter_fields = []
    related_fields = set()
    serializer_attributes = {}
    serializer_meta_attributes = {'model': _model, 'fields': serializer_fields, 'validators': []}
    filter_attributes = {'text_column': text_column}
    filter_meta_attributes = {'model': _model, 'fields': filter_fields, 'filter_overrides': filter_overrides}

    for field_name, _type in _model.__dict__.items():
        type_class = type(_type)
        # if it is a primary key field
        if field_name == 'id':
            serializer_attributes[field_name] = serializers.IntegerField(required=False)

        # model field that is directly inside one table
        if type_class == DeferredAttribute:
            field = _model._meta.get_field(field_name)
            field_type = type(field)
            serializer_fields.append(field_name)
            filter_fields.append(field_name)

            if field_type == CharField:
                text_column.append(field_name)

        if type_class == file_fields.ImageFileDescriptor:
            serializer_fields.append(field_name)

        # if it is a related field on another table, create nested serializer
        elif type_class in RELATED_FIELD_CLASS:
            try:
                field = _model._meta.get_field(field_name)
                field_type = type(field)
                serializer_fields.append(field_name)
                related_model = field.related_model
                related_fields.add(field.name)
                if field_type == ForeignKey:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(
                        allow_null=True, read_only=True)
                if field_type == ManyToManyField:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(many=True,
                                                                                                         read_only=True)
            except FieldDoesNotExist:
                pass

    # auto create serializer class using reflection
    serializer_meta_class = reflections.create_class(f"{_model.__name__}SerializerMeta", (type,),
                                                     serializer_meta_attributes)
    serializer_attributes['Meta'] = serializer_meta_class
    serializer_class = reflections.create_class(f"{_model.__name__}Serializer", (BaseSerializer,),
                                                serializer_attributes)

    # auto create filter class using reflection
    filter_meta_class = reflections.create_class(f"{_model.__name__}FilterMeta", (type,), filter_meta_attributes)
    filter_attributes['Meta'] = filter_meta_class
    filter_class = reflections.create_class(f"{_model.__name__}Filter", (BaseDjangoFilter,), filter_attributes)
    filter_backends = (filter_class,)

    field_tuples = tuple(serializer_fields)
    qs = _model.objects.all()

    # optimize prefetch for related fields
    if len(related_fields) > 0:
        qs = qs.select_related(*related_fields)

    view_set_attributes = {
        'queryset': qs,
        'serializer_class': serializer_class,
        'pagination_class': Pager,
        'filter_backends': filter_backends,
        'ordering_fields': field_tuples,
        'filterset_fields': field_tuples,
    }
    view_set_class = reflections.create_class(view_set_class_name, (BaseView,), view_set_attributes)
    return view_set_class
