from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from .models import *


# Create your views here.

@api_view(['GET'])
def get_sewa_detail(request):
    sewa_id = request.GET.get('sewa_id')

    if sewa_id:
        queryset = DetilSewa.objects.filter(sewa_id=int(sewa_id))
    else:
        queryset = DetilSewa.objects.all()
    queryset = queryset.select_related('sewa').select_related('buku').select_related('sewa__anggota')

    return Response([{
        'anggota': detilsewa.sewa.anggota.nama,
        'buku': detilsewa.buku.nama,
        'penerbit': detilsewa.buku.penerbit,
        'tanggal_terbit': detilsewa.buku.tanggal_terbit,
        'jumlahPinjam': detilsewa.jumlah,
        'id': detilsewa.buku.id,
        'id_detilsewa': detilsewa.id
    } for detilsewa in queryset])


@api_view(['POST'])
def save_sewa(request):
    body = json.loads(request.body)

    with transaction.atomic():
        sewa = Sewa.objects.update_or_create(anggota_id=body['anggota']['id'], tanggal_pinjam=body['tanggalPinjam'],
                                             tanggal_kembali=body['tanggalKembali'])
        for _buku in body['buku']:
            id_detilsewa = _buku.get('id_detilsewa')
            if id_detilsewa:
                detil = DetilSewa.objects.get(id=id_detilsewa)
                detil.jumlah = _buku['jumlahPinjam']
                detil.save()
            else:
                DetilSewa.objects.update_or_create(buku_id=_buku.get('id'), sewa_id=sewa[0].id, jumlah=_buku['jumlahPinjam'])

    return Response({'result': 'ok'})
