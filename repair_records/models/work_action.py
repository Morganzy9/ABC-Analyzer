from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Factory

class WorkAction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    factory = models.ForeignKey(
        Factory, verbose_name=_("Factory"), on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'work_action'
        verbose_name = 'Work Action'
        verbose_name_plural = 'Work Actions'