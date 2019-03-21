from django.db import models
from common import reflections
from common.models import BaseModel


# Create your models here.

class Vendor(BaseModel):
    class Meta:
        db_table = 'vendor'

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Device(BaseModel):
    class Meta:
        db_table = 'device'

    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default='1234')
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    #vendor = models.ManyToManyField(Vendor)
    location = models.CharField(max_length=255, blank=True)
    lat = models.DecimalField(max_digits=50, decimal_places=20, default=0, blank=True)
    long = models.DecimalField(max_digits=50, decimal_places=20, default=0, blank=True)
    status = models.CharField(max_length=15, default='Down')

    def __str__(self):
        return self.name


class DeviceReport(models.Model):
    class Meta:
        db_table = 'device_report'

    device = models.ForeignKey(Device, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=255)
    power = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    temperature = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device.name


classes = reflections.get_class(__name__)
