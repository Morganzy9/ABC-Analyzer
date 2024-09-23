from datetime import datetime

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from tasks.models import ScheduledTask


class ListTasksView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        tasks = ScheduledTask.objects.filter(factory__in=user.factories.all())

        date = request.GET.get("date")
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        tasks = tasks.filter(
            scheduled_date__date__lte=date,
            is_summarized=False,
        )

        data = [{
            'id': task.id,
            'factory': task.equipment.section.factory.name,
            'section': task.equipment.section.name,
            'equipment': task.equipment.name,
            'equipment_node': task.equipment_node.name,
            'performers': [performer.get_full_name() for performer in task.performers.all()],
            'repair_type': task.repair_type.codename,
            'work_type': task.work_type.name,
            'work_action': task.work_action.name,
            'allocated_time': task.allocated_time,
            'reason': task.reason,
            'comment': task.comment,
        }
            for task in tasks
        ]

        return JsonResponse(data, safe=False)
        

    def post(self, request):
        date = request.POST.get("date")
        draw = request.POST.get("draw", 0)

        tasks = ScheduledTask.objects.filter(factory__in=request.user.factories.all())
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()
        tasks = tasks.filter(
            scheduled_date__date__lte=date,
            is_summarized=False,
        )

        total = tasks.count()

        data = [{
            'id': task.id,
            'date': task.scheduled_date.strftime("%d/%m/%Y"),
            'section': task.equipment.section.name,
            'equipment_name': task.equipment.name,
            'equipment_node': task.equipment_node.name,
            'repair_type': task.repair_type.codename,
            'work_type': task.work_type.name,
            'work_action': task.work_action.name,
            'allocated_time': task.allocated_time,
            'reason': task.reason,
            'comment': task.comment,
        }
            for task in tasks
        ]

        response = {
            "draw": draw,
            "recordsTotal":total,
            "recordsFiltered": total,
            "data": data,
        }

        return JsonResponse(response, safe=False)
