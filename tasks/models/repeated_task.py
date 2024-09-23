from django.db import models
from django.utils.translation import gettext_lazy as _

from .task_base import TaskBase


class RepeatedTask(TaskBase):
    class Frequency(models.TextChoices):
        DAILY = "D", _("Daily")
        WEEKLY = "W", _("Weekly")
        MONTHLY = "M", _("Monthly")
        YEARLY = "Y", _("Yearly")

    frequency = models.CharField(
        _("Frequency"), max_length=1, choices=Frequency.choices
    )
    interval = models.PositiveIntegerField(_("Interval"))
    comment = models.TextField(_("Comment"), blank=True)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
