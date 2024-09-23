from django import forms

from .models import RepeatedTask, ScheduledTask
from repair_records.models import RepairRecord

class TaskAddRepeatedTaskForm(forms.ModelForm):
    class Meta:
        model = RepeatedTask
        fields = [field.name for field in RepeatedTask._meta.get_fields() if field.name not in ['id', 'performers', 'created_at', 'updated_at', 'repairrecord', 'scheduledtask']]

class TaskAddScheduledTaskForm(forms.ModelForm):
    class Meta:
        model = ScheduledTask
        fields = [field.name for field in ScheduledTask._meta.get_fields() if field.name not in ['id', 'performers', 'created_at', 'updated_at', 'scheduled_date']]

class TaskAddRepairRecordForm(forms.ModelForm):
    class Meta:
        model = RepairRecord
        fields = [field.name for field in RepairRecord._meta.get_fields() if field.name not in ['id', 'performers', 'created_at', 'updated_at', 'repairrecord']]
