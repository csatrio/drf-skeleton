from django.db import models


class RelatedManager(models.Manager):

    def __init__(self, *args):
        super(RelatedManager, self).__init__()
        self.related_fields = args

    def get_queryset(self):
        qs = super(RelatedManager, self).get_queryset()
        if self.related_fields:
            qs = qs.select_related(*self.related_fields)
        return qs


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
