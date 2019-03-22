from rest_framework.decorators import api_view
from rest_framework.response import Response

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
