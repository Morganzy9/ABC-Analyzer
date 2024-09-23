from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Factory, Section, User

class TaskBase(models.Model):
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
        'repair_records.Equipment', verbose_name=_("Equipment"), on_delete=models.CASCADE
    )
    equipment_node = models.ForeignKey(
        'repair_records.EquipmentNode', verbose_name=_("Node"), on_delete=models.CASCADE, null=True
    )

    repair_type = models.ForeignKey(
        'repair_records.RepairType', verbose_name=_("Repair Type"), on_delete=models.CASCADE
    )
    work_type = models.ForeignKey(
        'repair_records.WorkType', verbose_name=_("Work Type"), on_delete=models.CASCADE, null=True
    )
    work_action = models.ForeignKey(
        'repair_records.WorkAction', verbose_name=_("Work Action"), on_delete=models.CASCADE, null=True
    )

    master = models.ForeignKey(
        User,
        verbose_name=_("Master"),
        related_name="%(app_label)s_%(class)s_master",
        related_query_name="master",
        on_delete=models.SET_NULL,
        null=True,
    )
    performers = models.ManyToManyField(
        User,
        related_name="%(app_label)s_%(class)s_performers",
        related_query_name="performers",
        verbose_name=_("Performers"),
    )
    allocated_time = models.TimeField(verbose_name=_("Allocated Time"), null=True)

    reason = models.TextField(verbose_name=_("Reason"))

    class Meta:
        abstract = True
