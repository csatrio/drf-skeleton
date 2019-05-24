from collections.__init__ import OrderedDict

from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response


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
            ('rows', data)
        ]))
