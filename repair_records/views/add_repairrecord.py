
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission

from repair_records.forms import RepairRecordForm
from accounts.models import Section, User
from tasks.models import ScheduledTask
from repair_records.models import RepairType, Equipment, RepairRecord


class AddRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = 'repair_record/add.html'
    permission_required = 'repair_records.add_repairrecord'

    def get(self, request):
        user = request.user
        form = RepairRecordForm(request.POST or None, user=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user = request.user
        form = RepairRecordForm(request.POST or None, user=user)

        if form.is_valid():
            details_info_value = form.cleaned_data.get("details_info")
            print(f"Details Info from cleaned_data: {details_info_value}")  # Debug the cleaned data

            record = form.save()
            print(f"Saved record details_info: {record.details_info}")  # Check if it saved correctly
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging

        return redirect("add_repair_record")


class AddSelectionView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'repair_records.add_repairrecord'

    def get(self, request, option_type):
        id = request.GET.get("id")
        search = request.GET.get("search", "").strip()


        if id:
            id = int(id)
            if option_type == "equipment":
                options = Equipment.objects.filter(
                    section__pk=id).values_list('id', 'name')
            elif option_type == "section":
                options = Section.objects.filter(
                    factory__pk=id).values_list("id", "name")
            elif option_type == "master":
                perm = "add_repairrecord"
                perm_obj = Permission.objects.get(codename=perm)
                options = (
                    User.objects.filter(
                        Q(groups__permissions=perm_obj) | Q(user_permissions=perm_obj)
                    )
                    .filter(factories__pk=id)
                    .values_list("id", "first_name", "last_name")
                )
            elif option_type == "performers":
                print(f"Factory ID: {id}")
                options = User.objects.filter(
                    factories__pk=id, is_performer=True
                ).values_list("id", "first_name", "last_name")
                print(f"Performers Options: {list(options)}")
            elif option_type == "repair_type":
                options = RepairType.objects.filter(
                    factory__pk=id).values_list("id", "codename")
            else:
                return JsonResponse({'error': 'Invalid option type'}, status=400)

            data = {"options": list(options)}
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'ID not provided'}, status=400)

class GetRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'repair_records.add_repairrecord'

    def get(self, request, id):
        try:
            record = ScheduledTask.objects.get(pk=id)
        except RepairRecord.DoesNotExist:
            return JsonResponse({'error': _('Record not found')}, status=404)

        if record.master != request.user and not request.user.is_superuser:
            return JsonResponse({'error': _('You are not allowed to view this record')}, status=403)

        if not record.is_summarized:
            return JsonResponse({'error': _('Record is not summarized')}, status=400)

        data = {
            'id': record.id,
            'factory': (record.factory.pk, record.factory.name),
            'section': (record.section.pk, record.section.name),
            'equipment': (record.equipment.pk, record.equipment.name),
            'equipment_node': (record.equipment_node.pk, record.equipment_node.name),
            'master': (record.master.pk, record.master.get_full_name()),
            'performers': [(performer.pk, performer.get_full_name()) for performer in record.performers.all()],
            'repair_type': (record.repair_type.pk, record.repair_type.codename),
            'work_type': (record.work_type.pk, record.work_type.name),
            'work_action': (record.work_action.pk, record.work_action.name),
            'allocated_time': record.allocated_time,
            'reason': record.reason,
            "details_info": record.details_info,
        }
        return JsonResponse(data)
