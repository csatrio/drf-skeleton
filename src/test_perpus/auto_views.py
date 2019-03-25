from .auto_serializer_filter import *
from common.components import BaseView, Pager


class AnggotaViewSet(BaseView):
	queryset = Anggota.objects.all()
	serializer_class = AnggotaSerializer
	pagination_class = Pager
	filter_backends = (AnggotaFilter,)
	ordering_fields = ('nama', 'alamat', 'umur', 'id')
	filterset_fields = ('nama', 'alamat', 'umur', 'id')


class BukuViewSet(BaseView):
	queryset = Buku.objects.all()
	serializer_class = BukuSerializer
	pagination_class = Pager
	filter_backends = (BukuFilter,)
	ordering_fields = ('nama', 'penerbit', 'tanggal_terbit', 'id')
	filterset_fields = ('nama', 'penerbit', 'tanggal_terbit', 'id')


class DetilSewaViewSet(BaseView):
	queryset = DetilSewa.objects.all().select_related('buku', 'sewa__anggota', 'sewa')
	serializer_class = DetilSewaSerializer
	pagination_class = Pager
	filter_backends = (DetilSewaFilter,)
	ordering_fields = ('sewa_id', 'sewa', 'buku_id', 'buku', 'jumlah', 'id')
	filterset_fields = ('sewa_id', 'sewa', 'buku_id', 'buku', 'jumlah', 'id')


class SewaViewSet(BaseView):
	queryset = Sewa.objects.all().select_related('anggota')
	serializer_class = SewaSerializer
	pagination_class = Pager
	filter_backends = (SewaFilter,)
	ordering_fields = ('anggota_id', 'anggota', 'tanggal_pinjam', 'tanggal_kembali', 'id')
	filterset_fields = ('anggota_id', 'anggota', 'tanggal_pinjam', 'tanggal_kembali', 'id')


