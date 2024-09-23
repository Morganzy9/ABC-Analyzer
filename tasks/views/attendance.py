from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from accounts.models import Factory, User, Attendance


class AttendanceView(LoginRequiredMixin, View):
    def get(self, request):
        date = request.GET.get('date')
        user = request.user
        
        factories = user.factories.all()
        
        performers = User.objects.filter(
            factories__in=factories,
            is_performer=True,
            is_active=True,
        ).values(
            'id',
            'username',
            'first_name',
            'last_name',
        )

        # Get attendance
        if date:
            date = date
        else:
            date = datetime.now().date()
        
        attendance = Attendance.objects.filter(
            date=date,
            user__factories__in=factories,
        ).values(
            'user__id',
            'is_present',
            'shift_hours'
        )


        for performer in performers:
            performer['is_present'] = True
            for attend in attendance:
                if performer['id'] == attend['user__id']:
                    performer['is_present'] = attend['is_present']
                    performer['shift_hours'] = attend['shift_hours']
                    break

        data = list(performers)
        return JsonResponse(data, safe=False)
    
    def post(self, request):
        user_id = request.POST.get('id')
        is_present = request.POST.get('is_present')
        shift_hours = int(request.POST.get('shift_hours'))
        date = request.POST.get('date')

        if is_present == 'on':
            is_present = True
        else:
            is_present = False

        aa = Attendance.objects.update_or_create(
            user_id=user_id,
            date=date,
        )[0]
        
        aa.is_present = is_present
        aa.shift_hours = shift_hours
        aa.save()

        return JsonResponse({'status': 'ok'})