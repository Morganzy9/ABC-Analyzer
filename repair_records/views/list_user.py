import csv

from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity

from accounts.models import Factory, User
from repair_records.models import RepairRecord


class ListUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/list_user.html"
    permission_required = "accounts.view_user"

    def get(self, request):
        cols = {
            "name": _("Name"),
            "factory": _("Factory"),
            "type": _("Type"),
            "count": _("Count"),
        }

        user = request.user
        if user.is_superuser:
            factories = Factory.objects.all()
        else:
            factories = user.factories.all()
        factory_choices = factories.values_list("id", "name")

        return render(request, self.template_name, {"cols": cols, "factories": factory_choices})

    def post(self, request):
        user = request.user
        if user.is_superuser:
            records = User.objects.filter(is_superuser=False)
        else:
            records = User.objects.filter(
                is_superuser=False, factories__in=user.factories.all()
            )

        # Apply search filter
        filter_factory_ids = request.POST.getlist("factories[]")
        if filter_factory_ids and filter_factory_ids[0] == "":
            filter_factory_ids = filter_factory_ids[1:]

        if filter_factory_ids:
            records = records.filter(factories__id__in=filter_factory_ids)

        search_value = request.POST.get("search[value]", "")
        if search_value:
            records = (
                records.annotate(
                    full_name=Concat(
                        "first_name", Value(" "), "last_name", output_field=CharField()
                    )
                )
                .filter(
                    Q(factories__name__icontains=search_value)
                    | Q(full_name__icontains=search_value)
                    | Q(full_name__trigram_similar=search_value)
                )
            )

        total_count = User.objects.filter(is_superuser=False).count()
        records_filtered_count = records.distinct().count()

        # Pagination
        start = int(request.POST.get("start", 0))
        length = int(request.POST.get("length", 10))
        records = records.distinct()[start:start + length]

        data = [
            {
                "factory": ", ".join([x.name for x in record.factories.all()]),
                "name": f"<a class='link-dark link-underline' href='/repair-records/user/{record.id}/'>{record.first_name} {record.last_name}</a>",
                "type": _("Performer") if record.is_performer else _("Master"),
                "count": RepairRecord.objects.filter(
                    Q(master=record) | Q(performers__in=[record])
                )
                .distinct()
                .count(),
            }
            for record in records
        ]

        order_column_index = int(request.POST.get("order[0][column]", 0))
        order_direction = request.POST.get("order[0][dir]", "asc")

        def sort_key(record):
            column_name = list(record.keys())[order_column_index]
            return record[column_name]

        data = sorted(data, key=sort_key, reverse=(order_direction == "desc"))

        response_data = {
            "draw": int(request.POST.get("draw", 1)),
            "recordsTotal": total_count,
            "recordsFiltered": records_filtered_count,
            "data": data,
        }
        return JsonResponse(response_data)


class ListCSVUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "accounts.view_user"

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            records = User.objects.filter(is_superuser=False)
        else:
            records = User.objects.filter(
                is_superuser=False, factories__in=user.factories.all()
            )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="list_user.csv"'

        response.write("\ufeff".encode("utf-8"))
        csv_writer = csv.writer(response, delimiter=";")

        header_row = [field.name for field in User._meta.fields]
        header_row.append("type")
        header_row.append("factories")

        for row in [
            "password",
            "date_joined",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_performer",
            "last_login",
        ]:
            header_row.remove(row)

        csv_writer.writerow(header_row)

        print(header_row)

        def get_value(item, field):
            if field == "factories":
                return ", ".join([str(factory) for factory in item.factories.all()])
            if field == "type":
                if item.is_superuser:
                    return "admin"
                if item.is_performer:
                    return "performer"
                else:
                    return "master"
            return getattr(item, field)

        for item in records:
            data_row = [
                str(get_value(item, field))
                .replace(";", ".")
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("\r", " ")
                for field in header_row
            ]
            csv_writer.writerow(data_row)

        return response
