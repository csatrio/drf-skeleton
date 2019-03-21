import os
import itertools
import common.reflections as reflections
import common.mixins as serializer_mixin
from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict
from rest_framework import viewsets, generics, filters, mixins
from django_filters import rest_framework as rest_framework_filters
from django.db.models.query_utils import DeferredAttribute
from django.db.models import CharField, ForeignKey, ManyToManyField, Q
from django.conf import settings
from django.conf.urls import url as _url
from django.core.exceptions import FieldDoesNotExist
import django.db.models.fields.related_descriptors as related_descriptors

RELATED_FIELD_CLASS = reflections.get_class(related_descriptors.__name__)


class BaseView(viewsets.ModelViewSet, generics.ListAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    pass


class BaseSerializer(serializer_mixin.UniqueFieldsMixin, serializer_mixin.NestedCreateMixin,
                     serializer_mixin.NestedUpdateMixin):
    pass


class Pager(pagination.PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = settings.PAGE_SIZE_QUERY_PARAM
    max_page_size = settings.MAX_PAGE_SIZE
    per_page = page_size

    # to get query-per-page from request
    def paginate_queryset(self, queryset, request, view=None):
        val = request.GET.get(self.page_size_query_param)
        if val:
            val = int(val)
            if val != self.per_page and 0 < val <= self.max_page_size:
                self.per_page = val
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        total = self.page.paginator.count
        per_page = total if self.per_page > total else self.per_page
        if per_page == 0: per_page = 1
        total_page = total / per_page
        str_total_page = (str(total_page)).split('.')[1]

        last_page = int(total_page)
        if int(str_total_page) > 0: last_page += 1

        start_from = 1 + (self.page.number * per_page) - per_page
        if start_from < 1: start_from = 1

        end_at = (start_from + per_page) - 1
        if end_at > total: end_at = total

        if per_page >= total:
            start_from = 1
            end_at = total

        return Response(OrderedDict([
            ('total', total),
            ('per_page', per_page),
            ('current_page', self.page.number),
            ('last_page', last_page),
            ('next_page_url', self.get_next_link()),
            ('prev_page_url', self.get_previous_link()),
            ('from', start_from),
            ('to', end_at),
            ('data', data)
        ]))


class BaseDjangoFilter(filters.OrderingFilter, rest_framework_filters.FilterSet):
    text_column = ()
    id_column = 'id'

    def filter_queryset(self, request, queryset, view):
        req = request.GET.copy()
        q = req.get('q')
        _queryset = None
        ordering_q = req.get('ordering')

        # if it has these keys, remove it so it will not processed by next step of the filter
        BaseDjangoFilter.delete_key_if_exists(req, 'ordering', 'page', settings.PAGE_SIZE_QUERY_PARAM)

        if q is not None:
            _queryset = BaseDjangoFilter.filter_q(queryset, self.text_column, q)
        if req.get(self.id_column) is None:
            _queryset = BaseDjangoFilter.do_filter(req, self.text_column, queryset)
        else:
            _queryset = queryset.filter(id=req[self.id_column])

        # if it has ordering query, return filtered queryset
        if ordering_q:
            fields = [param.strip() for param in ordering_q.split(',')]
            ordering = self.remove_invalid_fields(_queryset, fields, view, request)
            if ordering:
                return _queryset.order_by(*ordering)

        return _queryset

    # for any http query that use 'q='
    @staticmethod
    def filter_q(queryset, search_field, value):

        if value:
            q_parts = value.split()

            # Permutation code copied from http://stackoverflow.com/a/12935562/119071

            list1 = search_field
            list2 = q_parts

            perms = [zip(x, list2) for x in itertools.permutations(list1, len(list2))]

            q_totals = Q()
            for perm in perms:
                q_part = Q()
                for p in perm:
                    q_part = q_part & Q(**{p[0] + '__icontains': p[1]})
                q_totals = q_totals | q_part

            queryset = queryset.filter(q_totals)
        return queryset

    # for any http get query, can be used with orm flags
    @staticmethod
    def do_filter(request, params, queryset):
        filter_list = []
        for key, value in request.items():
            # if key is not a text column
            if key not in params:
                filter_key = {key: value}
            # if key is a text column, search with contains option
            else:
                filter_key = {f"{key}__icontains": value}

            if filter_list:
                filter_list.append(filter_list[-1].filter(**filter_key))
            else:
                filter_list.append(queryset.filter(**filter_key))

        return filter_list[-1] if len(filter_list) else queryset.filter()

    @staticmethod
    def delete_key_if_exists(req, *args):
        for key in args:
            if req.get(key):
                del req[key]


def get_model_fields(_model):
    return tuple(field_name for field_name, _type in _model.__dict__.items() if
                 type(_type) == DeferredAttribute and 'id' not in field_name)


def nested_serializer(_model, related_fields=None):
    serializer_fields = []
    serializer_attributes = {}
    serializer_meta_attributes = {'model': _model, 'fields': serializer_fields}

    for field_name, _type in _model.__dict__.items():
        # if it is a model field
        if type(_type) == DeferredAttribute:
            serializer_fields.append(field_name)

        # if it is a related field, create nested serializer
        elif type(_type) in RELATED_FIELD_CLASS:
            try:
                field = _model._meta.get_field(field_name)
                field_type = type(field)
                serializer_fields.append(field_name)
                related_model = field.related_model
                if related_fields:
                    related_fields.append(f"{_model.__name__.lower()}__{field.name}")
                if field_type == ForeignKey:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)()
                if field_type == ManyToManyField:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(many=True)
            except FieldDoesNotExist:
                pass

    serializer_meta_class = type(f"{_model.__name__}SerializerMeta", (type,), serializer_meta_attributes)
    serializer_attributes['Meta'] = serializer_meta_class
    serializer_class = type(f"{_model.__name__}Serializer", (BaseSerializer,),
                            serializer_attributes)
    return serializer_class


def generic_view(_model):
    text_column = []
    serializer_fields = []
    filter_fields = []
    related_fields = []
    serializer_attributes = {}
    serializer_meta_attributes = {'model': _model, 'fields': serializer_fields}
    filter_attributes = {'text_column': text_column}
    filter_meta_attributes = {'model': _model, 'fields': filter_fields}

    for field_name, _type in _model.__dict__.items():
        # if it is a model field
        if type(_type) == DeferredAttribute:
            field = _model._meta.get_field(field_name)
            field_type = type(field)
            serializer_fields.append(field_name)
            filter_fields.append(field_name)

            if field_type == CharField:
                text_column.append(field_name)

        # if it is a related field, create nested serializer
        elif type(_type) in RELATED_FIELD_CLASS:
            try:
                field = _model._meta.get_field(field_name)
                field_type = type(field)
                serializer_fields.append(field_name)
                related_model = field.related_model
                related_fields.append(field.name)
                if field_type == ForeignKey:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)()
                if field_type == ManyToManyField:
                    serializer_attributes[field_name] = nested_serializer(related_model, related_fields)(many=True)
            except FieldDoesNotExist:
                pass

    # auto create serializer class using reflection
    serializer_meta_class = type(f"{_model.__name__}SerializerMeta", (type,), serializer_meta_attributes)
    serializer_attributes['Meta'] = serializer_meta_class
    serializer_class = type(f"{_model.__name__}Serializer", (BaseSerializer,),
                            serializer_attributes)

    # auto create filter class using reflection
    filter_meta_class = type(f"{_model.__name__}FilterMeta", (type,), filter_meta_attributes)
    filter_attributes['Meta'] = filter_meta_class
    filter_class = type(f"{_model.__name__}Filter", (BaseDjangoFilter,), filter_attributes)
    filter_backends = (filter_class,)

    field_tuples = tuple(serializer_fields)

    qs = _model.objects.all()

    # optimize prefetch for related fields
    qs = qs.prefetch_related(*related_fields)

    view_set_attributes = {
        'queryset': qs,
        'serializer_class': serializer_class,
        'pagination_class': Pager,
        'filter_backends': filter_backends,
        'ordering_fields': field_tuples,
        'filterset_fields': field_tuples,
    }
    view_set_class = type(f"{_model.__name__}ViewSet", (BaseView,), view_set_attributes)
    return view_set_class


def child_url_resolver(_file):
    current_folder = os.path.dirname(os.path.abspath(_file)).replace(os.getcwd(), '').replace(os.sep, '').strip()

    def url(*args):
        return _url(f"{current_folder}/{args[0]}", args[1])

    return url
