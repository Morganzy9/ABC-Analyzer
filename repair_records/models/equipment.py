from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Section

class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    codename = models.CharField(
        max_length=200, blank=True, verbose_name=_("Inventory Number")
    )
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    section = models.ForeignKey(
        Section, verbose_name=_("Section"), on_delete=models.CASCADE
    )

    prob_breaking = models.FloatField(default=0, verbose_name=_("Probab. of Breaking"))
    break_affect = models.FloatField(default=0, verbose_name=_("Affect of Breaking"))

    def __str__(self):
        return f"{self.codename} | {self.name}"

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipments")
