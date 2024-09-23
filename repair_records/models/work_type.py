from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Factory

class WorkType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    factory = models.ForeignKey(
        Factory, verbose_name=_("Section"), on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Work Type")
        verbose_name_plural = _("Work Types")
