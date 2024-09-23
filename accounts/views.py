from django.urls import reverse_lazy
from django.views.generic.edit import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.utils.translation import activate

from .forms import LoginForm, UserChangeForm
from .models import User


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        # Authenticate the user and log them in
        user = form.get_user()
        login(self.request, user)

        return super().form_valid(form)


class UserUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    success_url = reverse_lazy("home")
    template_name = "registration/change_form.html"


class HomeView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = request.user

        if user.is_superuser:
            return redirect("/admin")
        if user.has_perm('repair_records.summarize_repairrecord'):
            return redirect("/repair-records/summary")
        if user.has_perm('repair_records.view_repairrecord'):
            return redirect("/repair-records/list")
        if user.has_perm('repair_records.add_repairrecord'):
            return redirect("/repair-records/add")
        return redirect("/accounts/logout")


def change_language(request, language='ru'):
    '''
        A view that allows the user to change their preferred language
    '''

    if language in ['ru', 'uz', 'uz-CR', 'tr']:
        request.user.preferred_language = language
        request.user.save()
        activate(language)
    return redirect(request.META.get('HTTP_REFERER'))
