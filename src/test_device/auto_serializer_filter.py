from .models import *
from common.components import BaseDjangoFilter, BaseSerializer


class VendorSerializer(BaseSerializer):
	class Meta:
		model = Vendor
		fields = ['name', 'address']



class DeviceSerializer(BaseSerializer):
	class Meta:
		model = Device
		fields = ['name', 'password', 'vendor_id', 'vendor', 'location', 'lat', 'long', 'status', 'id']



class DeviceFilter(BaseDjangoFilter):
	text_column = ['name', 'password', 'location', 'status']
	class Meta:
		model = Device
		fields = ['name', 'password', 'vendor_id', 'location', 'lat', 'long', 'status', 'id']



class DeviceReportSerializer(BaseSerializer):
	class Meta:
		model = DeviceReport
		fields = ['device_id', 'device', 'status', 'power', 'flag', 'temperature', 'created', 'id']



class DeviceReportFilter(BaseDjangoFilter):
	text_column = ['status', 'power', 'flag']
	class Meta:
		model = DeviceReport
		fields = ['device_id', 'status', 'power', 'flag', 'temperature', 'created', 'id']



class VendorFilter(BaseDjangoFilter):
	text_column = ['name', 'address']
	class Meta:
		model = Vendor
		fields = ['name', 'address', 'id']



