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
        'jumlah': detilsewa.jumlah
    } for detilsewa in queryset])


@api_view(['POST'])
@transaction.atomic
def save_sewa(request):
    body = json.loads(request.body)
    sewa = Sewa(anggota_id=body['anggota']['id'], tanggal_pinjam=body['tanggalPinjam'],
                tanggal_kembali=body['tanggalKembali'])
    sewa.save()

    for _buku in body['buku']:
        detilsewa = DetilSewa(buku_id=_buku['id'], sewa=sewa, jumlah=_buku['jumlahPinjam'])
        detilsewa.save()

    return Response({'result': 'ok'})
