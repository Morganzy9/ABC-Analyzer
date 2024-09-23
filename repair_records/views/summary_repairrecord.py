import csv

from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity

from accounts.models import Factory
from repair_records.models import RepairType, Equipment, RepairRecord
from repair_records.utils import MatrixPdf, DayOfWeekPdf, RepairTypePdf, EquipmentPdf, MasterRepairPdf, merge_pdfs


class SummaryRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/summary.html"
    permission_required = "repair_records.summarize_repairrecord"

    def get(self, request):
        user = request.user
        if user.is_superuser:
            factory_list = Factory.objects.all().values_list("name", "id")
        else:
            factory_list = user.factories.all().values_list("name", "id")

        cols = {
            "factory": _("Factory"),
            "section": _("Section"),
            "equipment_codename": _("Equipment Codename"),
            "equipment_name": _("Equipment Name"),
            "prob_breaking": _("Probab. of Breaking"),
            "break_affect": _("Affect of Breaking"),
            "score": _("Score"),
        }

        user = request.user
        if user.is_superuser:
            factories = Factory.objects.all()
        else:
            factories = user.factories.all()
        factory_choices = factories.values_list("id", "name")

        return render(
            request, self.template_name, {"cols": cols, "factories": factory_choices, "factory_list": factory_list}
        )

    def post(self, request):
        user = request.user
        if user.is_superuser:
            records = Equipment.objects.all()
        else:
            records = Equipment.objects.filter(
                section__factory__in=user.factories.all()
            )

        # Apply search filter
        filter_factory_ids = request.POST.getlist("factories[]")
        if filter_factory_ids and filter_factory_ids[0] == "":
            filter_factory_ids = filter_factory_ids[1:]

        if filter_factory_ids:
            records = records.filter(section__factory_id__in=filter_factory_ids)

        search_value = request.POST.get("search[value]", "")
        if search_value:
            records = records.filter(
                Q(section__factory__name__icontains=search_value)
                | Q(section__name__icontains=search_value)
                | Q(codename__icontains=search_value)
                | Q(name__icontains=search_value)
                | Q(section__factory__name__trigram_similar=search_value)
                | Q(section__name__trigram_similar=search_value)
                | Q(name__trigram_similar=search_value)
            )

        # Apply color filter while generating data
        color = request.POST.get("color", "")

        def get_color(record):
            exp = round(
                round(record.prob_breaking, 2) + round(record.break_affect, 2), 2
            )

            if exp <= 0.7:
                return "green"
            elif exp > 1.5:
                return "red"
            return "yellow"

        print(color)

        data = [
            {
                "factory": record.section.factory.name,
                "section": record.section.name,
                "equipment_codename": record.codename,
                "equipment_name": f"<a class='link-dark link-underline' href='/repair-records/equipment/{record.id}/'>{record.name}</a>",
                "prob_breaking": round(record.prob_breaking, 2),
                "break_affect": round(record.break_affect, 2),
                "score": round(
                    round(record.prob_breaking, 2) + round(record.break_affect, 2), 2
                ),
            }
            for record in records.distinct()
            if color in get_color(record)
        ]

        # Sort the data based on the columns specified in request.POST
        order_column_index = int(request.POST.get("order[0][column]", 0))
        order_direction = request.POST.get("order[0][dir]", "asc")

        def sort_key(record):
            # Define a custom key function for sorting
            column_name = list(record.keys())[order_column_index]
            return record[column_name]

        # Sort the data based on the specified column and direction
        data = sorted(data, key=sort_key, reverse=(order_direction == "desc"))

        # Pagination
        start = int(request.POST.get("start", 0))
        length = int(request.POST.get("length", 10))

        total_count = len(data)

        data = data[start: start + length]

        response_data = {
            "draw": int(request.POST.get("draw", 1)),
            "recordsTotal": total_count,
            "recordsFiltered": total_count,
            "data": data,
        }
        return JsonResponse(response_data)


class SummaryCSVRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "repair_records.summarize_repairrecord"

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            records = Equipment.objects.all()
        else:
            records = Equipment.objects.filter(
                section__factory__in=user.factories.all()
            )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="summary_report.csv"'

        response.write("\ufeff".encode("utf-8"))
        csv_writer = csv.writer(response, delimiter=";")

        header_row = [field.name for field in Equipment._meta.fields]
        header_row.insert(4, "factory")
        csv_writer.writerow(header_row)

        for item in records:
            data_row = [
                str(getattr(item, field))
                .replace(";", ".")
                .replace("\n", " ")
                .replace("\t", " ")
                .replace("\r", " ")
                if field != "factory"
                else item.section.factory
                for field in header_row
            ]
            csv_writer.writerow(data_row)

        return response

class SummaryPDFRepairRecordView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = "repair_records.summarize_repairrecord"

    def get(self, request, factory_id):
        user = request.user
        if not user.is_superuser:
            factories = user.factories.all()

            if factory_id not in factories.values_list("id", flat=True):
                return HttpResponse(_("You do not have permission to access this page"), status=403)

        matrix_pdf = self.get_matrix_pdf(factory_id)
        dayofweek_pdf = self.get_dayofweek_pdf(factory_id)
        repairtype_pdf = self.get_repairtype_pdf(factory_id)
        equipment_pdf = self.get_equipment_pdf(factory_id)
        master_pdf = self.get_master_pdf(factory_id)

        pdf = merge_pdfs([matrix_pdf, dayofweek_pdf, repairtype_pdf, equipment_pdf, master_pdf])

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="summary.pdf"'
        response.write(pdf)

        return response

    def get_matrix_pdf(self, factory_id):
        records = Equipment.objects.filter(section__factory_id=factory_id)
        data = {record.codename: (record.prob_breaking, record.break_affect) for record in records}

        pdf = MatrixPdf(data)
        pdf = pdf.export_to_pdf()

        return pdf
    
    def get_dayofweek_pdf(self, factory_id):
        records = RepairRecord.objects.filter(factory__id=factory_id)
        data = {
            _("Monday"): 0,
            _("Tuesday"): 0,
            _("Wednesday"): 0,
            _("Thursday"): 0,
            _("Friday"): 0,
            _("Saturday"): 0,
            _("Sunday"): 0,
        }

        for record in records:
            data[_(record.start_time.strftime("%A"))] += 1

        pdf = DayOfWeekPdf(data)
        pdf = pdf.export_to_pdf()

        return pdf

    def get_repairtype_pdf(self, factory_id):
        records = RepairRecord.objects.filter(factory__id=factory_id)
        data = {}

        for record in records:
            codename = record.repair_type.codename
            data[codename] = data.get(codename, 0) + 1

        pdf = RepairTypePdf(data)
        pdf = pdf.export_to_pdf()

        return pdf

    def get_equipment_pdf(self, factory_id):
        records = RepairRecord.objects.filter(factory__id=factory_id)
        data = {}

        for record in records:
            name = record.equipment.name
            data[name] = data.get(name, 0) + 1

        pdf = EquipmentPdf(data)
        pdf = pdf.export_to_pdf()

        return pdf

    def get_master_pdf(self, factory_id):
        records = RepairRecord.objects.filter(factory__id=factory_id)
        data = {}

        for record in records:
            full_name = record.master.get_full_name()
            data[full_name] = data.get(full_name, 0) + 1

        pdf = MasterRepairPdf(data)
        pdf = pdf.export_to_pdf()

        return pdf

