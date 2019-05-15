from django.db import models

from common.models import BaseModel


# Create your models here.
# Add attribute is_automatic = False if you don't want to auto create admin and endpoint

class Person(BaseModel):
    class Meta:
        db_table = 'person'

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    age = models.IntegerField(default=0)
