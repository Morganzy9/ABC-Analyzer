from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Factory, Section, User


class RepairType(models.Model):
    # TODO: connect it to factories, and filter types based on
    # factory in add form and in admin page also.
    id = models.AutoField(primary_key=True)
    codename = models.CharField(max_length=5, verbose_name=_("CodeName"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    factory = models.ForeignKey(
        Factory, verbose_name=_("Section"), on_delete=models.CASCADE
    )

    def __str__(self):
        return self.codename

    class Meta:
        verbose_name = _("Repair Type")
        verbose_name_plural = _("Repair Types")


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
        return f"{self.name}"

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipments")


class EquipmentInactiveTime(models.Model):
    class ActiveType(models.TextChoices):
        ACTIVE = "A", _("Active")
        INACTIVE = "I", _("Inactive")

    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    datetime = models.DateTimeField(_("Start/End time of Inactivity"))
    active_type = models.CharField(
        _("Activity Type"), max_length=1, choices=ActiveType.choices
    )

    def __str__(self):
        return f"{self.active_type} {self.datetime}"

    class Meta:
        verbose_name = _("Equipment Inactive Time")
        verbose_name_plural = _("Equipment Inactive Times")


class RepairRecord(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    factory = models.ForeignKey(
        Factory, verbose_name=_("Factory"), on_delete=models.CASCADE
    )
    section = models.ForeignKey(
        Section, verbose_name=_("Section"), on_delete=models.CASCADE
    )

    equipment = models.ForeignKey(
        Equipment, verbose_name=_("Equipment"), on_delete=models.CASCADE
    )
    repair_type = models.ForeignKey(
        RepairType, verbose_name=_("Repair Type"), on_delete=models.CASCADE
    )
    master = models.ForeignKey(
        User,
        verbose_name=_("Master"),
        related_name="master",
        on_delete=models.SET_NULL,
        null=True,
    )
    performers = models.ManyToManyField(
        User, related_name="performers", verbose_name=_("Performers")
    )
    reason = models.TextField(verbose_name=_("Reason"))
    work_done = models.TextField(verbose_name=_("Work Done"))

    start_time = models.DateTimeField(verbose_name=_("Start Time"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))
    total_time = models.DurationField(
        verbose_name=_("Total Time"), blank=True, null=True
    )

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
