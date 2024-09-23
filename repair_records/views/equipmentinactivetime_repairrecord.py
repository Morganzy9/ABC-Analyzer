from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from repair_records.forms import EquipmentInactiveTimeForm


class EquipmentInactiveTimeView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "repair_record/add.html"
    permission_required = "repair_records.add_repairrecord"

    def get(self, request):
        return redirect(request.META.get("HTTP_REFERER"))

    def post(self, request):
        form = EquipmentInactiveTimeForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form)
            print(form.errors)

        return redirect(request.META.get("HTTP_REFERER"))
