from django.db import models
from django.utils.translation import gettext_lazy as _

from tasks.models import TaskBase, RepeatedTask

class RepairRecord(TaskBase):
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    task = models.ForeignKey(RepeatedTask, on_delete=models.SET_NULL, null=True, blank=True)

    work_done = models.TextField(verbose_name=_("Work Done"), blank=True, null=True)

    start_time = models.DateTimeField(verbose_name=_("Start Time"), blank=True, null=True)
    end_time = models.DateTimeField(verbose_name=_("End Time"), blank=True, null=True)
    total_time = models.DurationField(
        verbose_name=_("Total Time"), blank=True, null=True
    )
    details_info = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = _("Repair Record")
        verbose_name_plural = _("Repair Records")
        permissions = [("summarize_repairrecord", "Can summarize repair record")]

    def __str__(self):
        return f"{self.start_time} {self.equipment}"

    def save(self, *args, **kwargs):
        # Calculate the time difference
        if self.start_time and self.end_time:
            time_difference = self.end_time - self.start_time
            # Update the total_time field
            self.total_time = time_difference
        else:
            # Handle the case when either start_time or end_time is not set
            self.total_time = None

        super().save(*args, **kwargs)