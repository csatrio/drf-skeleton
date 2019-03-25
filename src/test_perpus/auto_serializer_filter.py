from .models import *
from common.components import BaseDjangoFilter, BaseSerializer


class AnggotaSerializer(BaseSerializer):
	class Meta:
		model = Anggota
		fields = ['nama', 'alamat', 'umur', 'id']



class AnggotaFilter(BaseDjangoFilter):
	text_column = ['nama', 'alamat']
	class Meta:
		model = Anggota
		fields = ['nama', 'alamat', 'umur', 'id']



class BukuSerializer(BaseSerializer):
	class Meta:
		model = Buku
		fields = ['nama', 'penerbit', 'tanggal_terbit', 'id']



class BukuFilter(BaseDjangoFilter):
	text_column = ['nama', 'penerbit']
	class Meta:
		model = Buku
		fields = ['nama', 'penerbit', 'tanggal_terbit', 'id']



class SewaSerializer(BaseSerializer):
	class Meta:
		model = Sewa
		fields = ['anggota_id', 'anggota', 'tanggal_pinjam', 'tanggal_kembali']



class DetilSewaSerializer(BaseSerializer):
	class Meta:
		model = DetilSewa
		fields = ['sewa_id', 'sewa', 'buku_id', 'buku', 'jumlah', 'id']



class DetilSewaFilter(BaseDjangoFilter):
	text_column = []
	class Meta:
		model = DetilSewa
		fields = ['sewa_id', 'buku_id', 'jumlah', 'id']



class SewaFilter(BaseDjangoFilter):
	text_column = []
	class Meta:
		model = Sewa
		fields = ['anggota_id', 'tanggal_pinjam', 'tanggal_kembali', 'id']



