from datetime import datetime
from weasyprint import HTML

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from accounts.models import User
from tasks.models import ScheduledTask


class SummaryTasksView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        factories = user.factories.all()

        # get date from request
        date = request.GET.get("date")
        if not date:
            date = datetime.now().date()

        repair_records = ScheduledTask.objects.filter(
            scheduled_date__date=date,
            is_summarized=True,
            factory__in=factories,
        ).distinct()

        for r in repair_records:
            print(r.id, end=" ")

        data = {
            "repair_records": [
                {
                    "id": repair_record.id,
                    "factory": repair_record.factory.name,
                    "section": repair_record.section.name,
                    "equipment": repair_record.equipment.name,
                    "equipment_node": repair_record.equipment_node.name,
                    "repair_type": repair_record.repair_type.codename,
                    "work_type": repair_record.work_type.name,
                    "work_action": repair_record.work_action.name,
                    "performers": [
                        {
                            "id": performer.id,
                            "name": performer.get_full_name(),
                            "username": performer.username,
                        }
                        for performer in repair_record.performers.all()
                    ],
                    "allocated_time": repair_record.allocated_time,
                    "reason": repair_record.reason,
                    "comment": repair_record.comment,
                }
                for repair_record in repair_records
            ]
        }

        data["shift_hours"] = factories.first().shift_hours

        print(data)
        return JsonResponse(data)

    @transaction.atomic
    def post(self, request):
        # get date, repair_record_id and performers id from request
        date = request.POST.get("date")
        repair_record_id = request.POST.get("id")
        performers = request.POST.getlist("performers[]")

        if not date:
            date = datetime.now().date()

        repair_record = ScheduledTask.objects.get(id=repair_record_id)
        repair_record.is_summarized = True
        repair_record.save()

        # get performers object by their id
        performers = User.objects.filter(id__in=performers)
        print(performers)
        repair_record.performers.clear()
        for performer in performers:
            repair_record.performers.add(performer)
        repair_record.save()
        print(repair_record.performers.all())

        data = {
            "success": "ok",
        }

        return JsonResponse(data)


class DiscardSummaryTasksView(LoginRequiredMixin, View):
    def post(self, request):
        # get repair_record_id from request
        repair_record_id = request.POST.get("id")

        repair_record = ScheduledTask.objects.get(id=repair_record_id)
        repair_record.is_summarized = False

        repair_record.performers.clear()
        repair_record.save()

        data = {
            "success": "ok",
        }

        return JsonResponse(data)


class SummaryPDFTasksView(LoginRequiredMixin, View):
    """generates pdf document for tasks summary, and returns it to download"""

    def get(self, request):
        user = request.user
        factories = user.factories.all()        

        # get date from request
        date = request.GET.get("date")
        if not date:
            date = datetime.now().date()

        repair_records = ScheduledTask.objects.filter(
            scheduled_date__date=date, is_summarized=True, factory__in=factories
        )

        print(repair_records)

        data = [
            [
                {
                    "id": repair_record.id,
                    "factory": repair_record.factory.name,
                    "section": repair_record.section.name,
                    "equipment": repair_record.equipment.name,
                    "equipment_node": repair_record.equipment_node.name,
                    "repair_type": repair_record.repair_type.codename,
                    "work_type": repair_record.work_type.name,
                    "work_action": repair_record.work_action.name,
                    "performers": repair_record.performers.all().count(),
                    "allocated_time": repair_record.allocated_time,
                    "reason": repair_record.reason,
                    "comment": repair_record.comment,
                }
                for repair_record in repair_records.filter(
                    repair_type__codename=repair_type
                )
            ]
            for repair_type in set(
                repair_record.repair_type.codename for repair_record in repair_records
            )
        ]

        data = {"date": date, "repair_records": data}

        html_string = render_to_string(
            "tasks/summary_pdf.html", {"data": data}
        )

        html = HTML(string=html_string)
        html.write_pdf(target="media/pdf/tasks_summary.pdf")

        fs = open("media/pdf/tasks_summary.pdf", "rb")
        response = HttpResponse(fs, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="tasks_summary.pdf"'

        return response
