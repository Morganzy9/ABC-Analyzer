import csv

from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta, timezone
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.search import TrigramSimilarity

from accounts.models import Factory
from repair_records.models import RepairRecord


class ListRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/list.html"
    permission_required = "repair_records.view_repairrecord"

    def get(self, request):
        user = request.user
        if user.is_superuser:
            factories = Factory.objects.all()
        else:
            factories = user.factories.all()
        factory_choices = factories.values_list("id", "name")

        return render(request, self.template_name, {"factories": factory_choices})

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            records = RepairRecord.objects.all()
        else:
            records = RepairRecord.objects.filter(factory__in=user.factories.all())

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

        # Apply date range filter
        filter_factory_ids = request.POST.getlist("factories[]")
        if filter_factory_ids and filter_factory_ids[0] == "":
            filter_factory_ids = filter_factory_ids[1:]

        if filter_factory_ids:
            records = records.filter(section__factory_id__in=filter_factory_ids)

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        start_datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
        end_datetime = datetime.now(timezone.utc)

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
            records = records.filter(created_at__range=(start_datetime, end_datetime))

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


        if start < 0:
            start = 0
        if length <= 0:
            length = 10

        total_count = records.count()

        if start >= total_count:
            start = max(total_count - length, 0)

        records = records[start: start + length]

        data = [
            {
                "start_time": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": record.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "factory": record.factory.name,
                "section": record.section.name,
                "master": f"{record.master.first_name} {record.master.last_name}" if record.master else "No master",
                "performers": ",".join(f"{x.first_name} {x.last_name}" for x in record.performers.all()),
                "equipment_codename": record.equipment.codename,
                "equipment_name": record.equipment.name,
                "repair_type": record.repair_type.codename,
                "reason": record.reason,
                "work_done": record.work_done,
                "total_time": self.format_total_time(record.total_time),
            }
            for record in records
        ]

        response_data = {
            "draw": int(request.POST.get("draw", 1)),
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": data,
        }
        return JsonResponse(response_data)

    def format_total_time(self, total_time):
        """Format the total time in 'X ч. Y мин. Z сек.' format."""
        days = total_time.days
        hours, remainder = divmod(total_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        formatted_time = []
        if days > 0:
            formatted_time.append(f"{days} д.")

        if hours > 0:
            formatted_time.append(f"{hours} ч.")

        if minutes > 0:
            formatted_time.append(f"{minutes} мин.")

        if seconds > 0 or not formatted_time:
            formatted_time.append(f"{seconds} сек.")

        return " ".join(formatted_time)


class ListCSVRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "repair_records.view_repairrecord"

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            records = RepairRecord.objects.all()
        else:
            records = RepairRecord.objects.filter(factory__in=user.factories.all())

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="list_report.csv"'

        response.write("\ufeff".encode("utf-8"))
        csv_writer = csv.writer(response, delimiter=";")

        header_row = [field.name for field in RepairRecord._meta.fields]
        header_row.insert(8, "performers")
        csv_writer.writerow(header_row)

        for item in records:
            data_row = [
                str(getattr(item, field))
                .replace(";", ".")
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("\r", " ")
                if field != "performers"
                else ", ".join([str(performer) for performer in item.performers.all()])
                for field in header_row
            ]
            csv_writer.writerow(data_row)

        return response
