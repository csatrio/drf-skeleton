from .models import *
from common.components import BaseDjangoFilter, BaseSerializer


class PersonSerializer(BaseSerializer):
	class Meta:
		model = Person
		fields = ['name', 'address', 'age', 'id']



class PersonFilter(BaseDjangoFilter):
	text_column = ['name', 'address']
	class Meta:
		model = Person
		fields = ['name', 'address', 'age', 'id']



