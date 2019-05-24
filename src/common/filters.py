import itertools

from django.conf import settings
from django.db.models import Q
from django_filters import rest_framework as rest_framework_filters
from rest_framework import filters


class BaseDjangoFilter(filters.OrderingFilter, rest_framework_filters.FilterSet):
    text_column = ()
    id_column = 'id'

    def filter_queryset(self, request, queryset, view):
        req = request.GET.copy()
        q = req.get('q')
        _queryset = None
        ordering_q = req.get('ordering')

        # if it has these keys, remove it so it will not processed by next step of the filter
        BaseDjangoFilter.delete_key_if_exists(req, 'q', 'ordering', 'page', 'format', settings.PAGE_SIZE_QUERY_PARAM)

        if q is not None:
            _queryset = BaseDjangoFilter.filter_q(queryset, self.text_column, q)
        elif req.get(self.id_column) is None:
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
