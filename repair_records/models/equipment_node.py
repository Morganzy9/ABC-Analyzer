from django.db import models
from django.utils.translation import gettext_lazy as _

from .equipment import Equipment

class EquipmentNode(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    equipment = models.ForeignKey(
        Equipment, verbose_name=_("Equipment"), on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Equipment Node")
        verbose_name_plural = _("Equipment Nodes")
