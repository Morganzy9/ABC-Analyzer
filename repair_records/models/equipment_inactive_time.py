from django.db import models
from django.utils.translation import gettext_lazy as _

from .equipment import Equipment

class EquipmentInactiveTime(models.Model):
    class ActiveType(models.TextChoices):
        ACTIVE = "A", _("Active")
        INACTIVE = "I", _("Inactive")

    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    datetime = models.DateTimeField(_("Start/End time fo Inactivity"))
    active_type = models.CharField(
        _("Activity Type"), max_length=1, choices=ActiveType.choices
    )

    def __str__(self):
        return f"{self.active_type} {self.datetime}"

    class Meta:
        verbose_name = _("Equipment Inactive Time")
        verbose_name_plural = _("Equipment Inactive Times")
