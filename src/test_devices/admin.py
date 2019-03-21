from django.contrib import admin
from .models import classes
from common.components import get_model_fields

# Register your models here.
for model in classes:
    model_admin = type(f"{model.__name__}Admin", (admin.ModelAdmin,), {'list_display': get_model_fields(model)})
    admin.site.register(model, model_admin)
