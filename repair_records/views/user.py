from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

from accounts.models import Factory, User
from repair_records.models import RepairRecord


class UserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/user.html"
    permission_required = "accounts.view_user"

    def get(self, request, id):
        user = User.objects.get(id=id)
        
        if user.is_superuser:
            factories = Factory.objects.all()
        else:
            factories = user.factories.all()
        
        factory_choices = factories.values_list("id", "name")


        data = {
            "name": user,
            "factories": factory_choices,
        }

        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        records = RepairRecord.objects.filter(
            Q(master__id=id) | Q(performers__id__in=[id])
        ).distinct()
        if not records.exists():
            response_data = {
                "draw": int(request.POST.get("draw", 1)),
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "type_count": {},
                "graph": {},
                "data": {},
            }

            return JsonResponse(response_data)

        # Apply date range filter
        filter_factory_ids = request.POST.getlist("factories[]")
        if filter_factory_ids and filter_factory_ids[0] == "":
            filter_factory_ids = filter_factory_ids[1:]

        if filter_factory_ids:
            records = records.filter(section__factory_id__in=filter_factory_ids)

        if not records.exists():
            response_data = {
                "draw": int(request.POST.get("draw", 1)),
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "type_count": {},
                "graph": {},
                "data": {},
            }

            return JsonResponse(response_data)
        
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        start_datetime = records.earliest("created_at").start_time
        end_datetime = records.latest("created_at").start_time

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

        print(start_datetime, end_datetime)

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
                Q(factory__name__icontains=search_value)
                | Q(section__name__icontains=search_value)
                | Q(master__full_name__icontains=search_value)
                | Q(performers__full_name__icontains=search_value)
                | Q(equipment__codename__icontains=search_value)
                | Q(equipment__name__icontains=search_value)
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
                "factory": record.factory.name,
                "section": record.section.name,
                "master": f"{record.master.first_name} {record.master.last_name}",
                "performers": ",".join(
                    f"{x.first_name} {x.last_name}" for x in record.performers.all()
                ),
                "equipment_codename": record.equipment.codename,
                "equipment_name": record.equipment.name,
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
            for record in records.distinct()
        ]

        response_data = {
            "draw": int(request.POST.get("draw", 1)),
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "type_count": type_count,
            "graph": graph,
            "data": data,
        }

        return JsonResponse(response_data)
