from base64 import b64decode

from django.db import models
from django.utils.encoding import force_bytes


class BinaryTextField(models.Field):
    def to_python(self, value):
        if isinstance(value, str):
            return value
        else:
            return memoryview(b64decode(force_bytes(value)))

    def get_internal_type(self):
        return 'BinaryField'

    def __str__(self):
        return 'BinaryTextField'
