from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

from repair_records.models import Equipment, EquipmentInactiveTime, RepairRecord


class EquipmentView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/equipment.html"
    permission_required = "repair_records.summary_repairrecord"

    def get(self, request, id):
        equipment = Equipment.objects.get(id=id)
        data = {
            "id": equipment.id,
            "name": equipment.name,
            "codename": equipment.codename,
            "section": equipment.section,
            "factory": equipment.section.factory,
            "prob_breaking": equipment.prob_breaking,
            "break_affect": equipment.break_affect,
        }

        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        records = RepairRecord.objects.filter(equipment__id=id)
        if not records.exists():
            response_data = {
                "draw": int(request.POST.get("draw", 1)),
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "type_count": {},
                "inactivity": {},
                "graph": {},
                "data": {},
            }

            return JsonResponse(response_data)

        # Apply date range filter
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        start_datetime = records.earliest("created_at").start_time
        end_datetime = timezone.now()

        if start_date != "":
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        if end_date != "":
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        elif start_datetime > end_datetime:
            end_datetime = start_datetime

        end_datetime += timedelta(days=1)

        if start_datetime <= end_datetime:
            records = records.filter(start_time__range=(start_datetime, end_datetime))

        # Get repair types
        repair_types = records.values_list("repair_type__codename").distinct()
        type_count = {
            x[0]: records.filter(repair_type__codename=x[0]).count()
            for x in repair_types
        }

        days_diff = (end_datetime - start_datetime).days

        graph = {
            x[0]: [
                {
                    "date": (start_datetime + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "count": records.filter(
                        repair_type__codename=x[0],
                        start_time__date=start_datetime + timedelta(days=i),
                    ).count(),
                }
                for i in range(days_diff + 1)
            ]
            for x in repair_types
        }

        # Fetch inactivity data
        inactivity_data = EquipmentInactiveTime.objects.filter(
            equipment__id=id,
            datetime__range=(start_datetime, end_datetime),
        ).values("active_type", "datetime")

        inactivity_periods = []
        for entry in inactivity_data:
            if entry["active_type"] == "I":
                inactivity_periods.append({"started_at": entry["datetime"]})
            elif entry["active_type"] == "A" and len(inactivity_periods):
                inactivity_periods[-1]["ended_at"] = entry["datetime"]

        print(inactivity_periods)
        inactivity = {}
        for entry in inactivity_periods:
            if "ended_at" not in entry:
                entry["ended_at"] = timezone.now()

            if entry["started_at"].date() == entry["ended_at"].date():
                inactivity[entry["started_at"].strftime("%Y-%m-%d")] = (
                    entry["ended_at"] - entry["started_at"] + entry["started_at"]
                ).strftime("%H:%M")

            else:
                midnight = entry["started_at"].replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                inactivity[entry["started_at"].strftime("%Y-%m-%d")] = (
                    midnight + timedelta(days=1) - entry["started_at"] + midnight
                ).strftime("%H:%M")

                temp = entry["started_at"].date()
                while temp < entry["ended_at"].date():
                    inactivity[temp.strftime("%Y-%m-%d")] = "24:00"
                    temp += timedelta(days=1)

                inactivity[entry["ended_at"].strftime("%Y-%m-%d")] = entry[
                    "ended_at"
                ].strftime("%H:%M")

        # Apply search filter
        search_value = request.POST.get("search[value]", "")
        if search_value:
            records = records.annotate(
                master__full_name=Concat(
                    "master__first_name",
                    Value(" "),
                    "master__last_name",
                    output_field=CharField(),
                ),
                performers__full_name=Concat(
                    "performers__first_name",
                    Value(" "),
                    "performers__last_name",
                    output_field=CharField(),
                ),
            ).filter(
                Q(master__full_name__icontains=search_value)
                | Q(performers__full_name__icontains=search_value)
                | Q(reason__icontains=search_value)
                | Q(work_done__icontains=search_value)
                | Q(repair_type__codename__icontains=search_value)
            )

        # Sorting
        sorting_column_index = int(request.POST.get("order[0][column]", 0))
        sorting_column_name = request.POST.get(
            f"columns[{sorting_column_index}][data]", "id"
        )
        sorting_direction = request.POST.get("order[0][dir]", "asc")

        if sorting_column_name == "date":
            sorting_column_name = "created_at"
        elif sorting_column_name == "equipment_codename":
            sorting_column_name = "equipment__codename"
        elif sorting_column_name == "equipment_name":
            sorting_column_name = "equipment__name"

        # Construct the sorting expression dynamically
        if sorting_direction == "desc":
            sorting_expression = "-" + sorting_column_name
        else:
            sorting_expression = sorting_column_name

        records = records.order_by(sorting_expression)

        # Pagination
        start = int(request.POST.get("start", 0))
        length = int(request.POST.get("length", 10))

        total_count = records.count()

        records = records[start: start + length]

        # Prepare the data for DataTables
        data = [
            {
                "date": record.created_at.strftime("%Y-%m-%d"),
                "master": f"{record.master.first_name} {record.master.last_name}",
                "performers": ",".join(
                    f"{x.first_name} {x.last_name}" for x in record.performers.all()
                ),
                "repair_type": record.repair_type.codename,
                "reason": record.reason,
                "work_done": record.work_done,
                "total_time": f"{int(record.total_time.days)}days "
                if record.total_time.days > 0
                else ""
                f"{int(record.total_time.seconds // 3600)}:"
                f"{int((record.total_time.seconds % 3600) // 60)}:"
                f"{int(record.total_time.seconds % 60)}",
            }
            for record in records
        ]

        response_data = {
            "draw": int(request.POST.get("draw", 1)),
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "type_count": type_count,
            "graph": graph,
            "inactivity": inactivity,
            "data": data,
        }

        return JsonResponse(response_data)
