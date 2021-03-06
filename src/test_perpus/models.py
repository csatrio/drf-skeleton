from django.db import models, transaction

from common.models import BaseModel, RelatedManager


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


class Kategori(BaseModel):
    class Meta:
        db_table = 'kategori'

    nama_kategori = models.CharField(max_length=255)

    def __str__(self):
        return self.nama_kategori


class Buku(BaseModel):
    class Meta:
        db_table = 'buku'

    kategori = models.ForeignKey(Kategori, on_delete=models.DO_NOTHING, default=-1)
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
    objects = RelatedManager('anggota')
    inlines = ['DetilSewa']

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic():
            for detilsewa in self.detilsewa_set.all():
                detilsewa.delete()
        super(Sewa, self).delete()

    def __str__(self):
        return self.anggota.nama


class DetilSewa(BaseModel):
    class Meta:
        db_table = 'detilsewa'

    sewa = models.ForeignKey(Sewa, on_delete=models.DO_NOTHING)
    buku = models.ForeignKey(Buku, on_delete=models.DO_NOTHING)
    jumlah = models.IntegerField(default=0)
    objects = RelatedManager('buku')

    def __str__(self):
        return f"Jumlah Pinjam: {self.jumlah}"
