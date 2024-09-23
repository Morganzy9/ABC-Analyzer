import copy
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from django.views import View
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.http import JsonResponse

from accounts.models import Factory, Section
from repair_records.models import RepairType, WorkType, WorkAction, Equipment, EquipmentNode
from tasks.models import ScheduledTask
from tasks.forms import TaskAddRepeatedTaskForm, TaskAddScheduledTaskForm

class AddTaskView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'repair_records.add_repairrecord'

    # save the task to RepeatedTask model using forms
    def post(self, request):
        post = request.POST.copy()
        if post.get("frequency") == "1":
            post["frequency"] = "D"
            post["interval"] = "1"
        elif post.get("frequency") == "7":
            post["frequency"] = "W"
            post["interval"] = "1"
        elif post.get("frequency") == "10":
            post["frequency"] = "D"
            post["interval"] = "10"
        elif post.get("frequency") == "14":
            post["frequency"] = "W"
            post["interval"] = "2"
        elif post.get("frequency") == "30":
            post["frequency"] = "M"
            post["interval"] = "1"
        elif post.get("frequency") == "90":
            post["frequency"] = "M"
            post["interval"] = "3"
        elif post.get("frequency") == "180":
            post["frequency"] = "M"
            post["interval"] = "6"
        elif post.get("frequency") == "365":
            post["frequency"] = "Y"
            post["interval"] = "1"

        post["performers"] = [""]

        form = TaskAddScheduledTaskForm(post)
        if form.is_valid():

            if post.get("frequency") != "0":
                task = TaskAddRepeatedTaskForm(post)
                if form.is_valid():
                    task = task.save()

                    form.task = task


            record = form.save()
            date = post['date'].split("-")
            scheduled_date = datetime.today()
            scheduled_date = scheduled_date.replace(
                year=int(date[0]), month=int(date[1]), day=int(date[2])
            )

            record.scheduled_date = scheduled_date
            record.master = request.user
            record.save()

            if post.get("frequency") != "0":
                self.bulk_repair_record(task, record)

            data = {
                'id': record.id,
                'factory': record.factory.name,
                'section': record.section.name,
                'equipment': record.equipment.name,
                'equipment_node': record.equipment_node.name,
                'repair_type': record.repair_type.codename,
                'work_type': record.work_type.name,
                'work_action': record.work_action.name,
                'allocated_time': record.allocated_time,
                'reason': record.reason,
                'comment': record.comment,
            }
            return JsonResponse(data)
        else:
            print(form.errors)
            return JsonResponse(form.errors, status=400)
        
    # get the next date of the task
    def get_next_date(self, task, record):
        if task.frequency == "D":
            return record.scheduled_date + timedelta(days=task.interval)
        elif task.frequency == "W":
            return record.scheduled_date + timedelta(weeks=task.interval)
        elif task.frequency == "M":
            return record.scheduled_date + relativedelta(months=task.interval)
        elif task.frequency == "Y":
            return record.scheduled_date + relativedelta(years=task.interval)
        else:
            return record.scheduled_date + timedelta(years=1)

    def insert_repair_record(self, task, record):
        new_record = ScheduledTask.objects.create(
            factory=record.factory,
            section=record.section,
            equipment=record.equipment,
            equipment_node=record.equipment_node,
            master=record.master,
            repair_type=record.repair_type,
            work_type=record.work_type,
            work_action=record.work_action,
            allocated_time=record.allocated_time,
            reason=record.reason,
            comment=record.comment,
        )
        new_record.performers.set(record.performers.all())
        new_record.save()

        scheduled_date=self.get_next_date(task, record)
        new_record.scheduled_date = scheduled_date
        new_record.save()

        return new_record

    def bulk_repair_record(self, task, record):
        scheduled_date = record.scheduled_date
        next_date = self.get_next_date(task, record)
        while next_date < scheduled_date + relativedelta(months=2):
            record = self.insert_repair_record(task, record)
            next_date = self.get_next_date(task, record)

class AddSelectionView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'repair_records.add_repairrecord'

    def get(self, request, option_type):
        user = request.user
        id = request.GET.get("id")

        if option_type == "factory" and user.is_superuser:
            options = Factory.objects.values_list("id", "name")
        elif option_type == "factory":
            options = user.factories.values_list("id", "name")

        elif option_type == "section":
            options = Section.objects.filter(
                factory__pk=id).values_list("id", "name")
            
        elif option_type == "equipment":
            options = Equipment.objects.filter(
                section__pk=id).values_list('id', 'name')
        elif option_type == "equipment_node":
            options = EquipmentNode.objects.filter(
                equipment__pk=id).values_list('id', 'name')
        
        elif option_type == "repair_type":
            options = RepairType.objects.filter(
                factory__pk=id).values_list("id", "codename")
        elif option_type == "work_type":
            options = WorkType.objects.filter(
                factory__pk=id).values_list("id", "name")
        elif option_type == "work_action":
            options = WorkAction.objects.filter(
                factory__pk=id).values_list("id", "name")

        else:
            return JsonResponse({'error': 'Invalid option type'}, status=400)

        data = {"options": list(options)}
        return JsonResponse(data)
