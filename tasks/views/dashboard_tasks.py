from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.shortcuts import render


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/dashboard.html'

    def get(self, request):
        user = request.user

        if not user.factories.exists():
            return HttpResponse(_('You can not access this page, because you are not connected to a factory.'))

        if not user.has_perm('repair_records.add_repairrecord'):
            return HttpResponse(_('You can not access this page, because you do not have the permission to add repair records.'))

        shift_hours = user.factories.first().shift_hours

        data = {
            'shift_hours': shift_hours,
        }

        return render(request, self.template_name, data)

