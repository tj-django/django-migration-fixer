from django.utils.translation import gettext_lazy as _

from django.db import models


class TestModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=500)
    age = models.PositiveIntegerField(default=50)
    active = models.BooleanField(null=True)

    class Meta:
        verbose_name = _("test model")
        verbose_name_plural = _("test models")

    def __str__(self):
        return str(_(self.name))

    __repr__ = __str__
