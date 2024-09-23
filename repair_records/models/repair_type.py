from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Factory

class RepairType(models.Model):
    # TODO: connect it to factories, and filter types based on
    # factory in add form and in admin page also.
    id = models.AutoField(primary_key=True)
    codename = models.CharField(max_length=5, verbose_name=_("CodeName"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    factory = models.ForeignKey(
        Factory, verbose_name=_("Section"), on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.codename}"

    class Meta:
        verbose_name = _("Repair Type")
        verbose_name_plural = _("Repair Types")
