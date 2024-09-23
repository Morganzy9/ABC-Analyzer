from django.db import models
from django.utils.translation import gettext_lazy as _

from .task_base import TaskBase
from .repeated_task import RepeatedTask

class ScheduledTask(TaskBase):
    comment = models.TextField(_("Comment"), blank=True)
    is_summarized = models.BooleanField(default=False)
    scheduled_date = models.DateTimeField(null=True)

    task = models.ForeignKey(RepeatedTask, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        verbose_name = _("Scheduled Task")
        verbose_name_plural = _("Scheduled Tasks")