from .auto_serializer_filter import *
from common.components import BaseView, Pager


class DeviceViewSet(BaseView):
	queryset = Device.objects.all().select_related('vendor')
	serializer_class = DeviceSerializer
	pagination_class = Pager
	filter_backends = (DeviceFilter,)
	ordering_fields = ('name', 'password', 'vendor_id', 'vendor', 'location', 'lat', 'long', 'status', 'id')
	filterset_fields = ('name', 'password', 'vendor_id', 'vendor', 'location', 'lat', 'long', 'status', 'id')


class DeviceReportViewSet(BaseView):
	queryset = DeviceReport.objects.all().select_related('device', 'device__vendor')
	serializer_class = DeviceReportSerializer
	pagination_class = Pager
	filter_backends = (DeviceReportFilter,)
	ordering_fields = ('device_id', 'device', 'status', 'power', 'flag', 'temperature', 'created', 'id')
	filterset_fields = ('device_id', 'device', 'status', 'power', 'flag', 'temperature', 'created', 'id')


class VendorViewSet(BaseView):
	queryset = Vendor.objects.all()
	serializer_class = VendorSerializer
	pagination_class = Pager
	filter_backends = (VendorFilter,)
	ordering_fields = ('name', 'address', 'id')
	filterset_fields = ('name', 'address', 'id')


