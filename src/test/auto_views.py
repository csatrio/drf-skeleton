from .auto_serializer_filter import *
from common.components import BaseView, Pager


class PersonViewSet(BaseView):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer
	pagination_class = Pager
	filter_backends = (PersonFilter,)
	ordering_fields = ('name', 'address', 'age', 'id')
	filterset_fields = ('name', 'address', 'age', 'id')


