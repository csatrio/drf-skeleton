from django.db import models
from common import reflections
from common.models import BaseModel


# Create your models here.
# Add attribute is_automatic = False if you don't want to auto create admin and endpoint

class Anggota(BaseModel):
    class Meta:
        db_table = 'anggota'

    nama = models.CharField(max_length=255)
    alamat = models.CharField(max_length=255)
    umur = models.IntegerField(default=0)

    def __str__(self):
        return self.nama


class Buku(BaseModel):
    class Meta:
        db_table = 'buku'

    nama = models.CharField(max_length=255)
    penerbit = models.CharField(max_length=255)
    tanggal_terbit = models.DateField()

    def __str__(self):
        return self.nama


class Sewa(BaseModel):
    class Meta:
        db_table = 'sewa'

    anggota = models.ForeignKey(Anggota, on_delete=models.DO_NOTHING)
    tanggal_pinjam = models.DateField()
    tanggal_kembali = models.DateField()

    def __str__(self):
        return self.anggota.nama


class DetilSewa(BaseModel):
    class Meta:
        db_table = 'detilsewa'

    sewa = models.ForeignKey(Sewa, on_delete=models.DO_NOTHING)
    buku = models.ForeignKey(Buku, on_delete=models.DO_NOTHING)
    jumlah = models.IntegerField(default=0)


classes = reflections.get_classes(__name__)
