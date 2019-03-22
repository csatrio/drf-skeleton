from django.contrib import admin
from .models import classes
import common.reflections as reflections

# Register your models here.
reflections.auto_register_model_admin(classes)
