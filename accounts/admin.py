# admin.py
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect

from .forms import UserCreationForm, UserChangeForm, GroupChangeForm
from .models import Factory, Section, User, Attendance

admin.site.site_url = "/repair-records/list"


class FactoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(Factory, FactoryAdmin)

admin.site.register(Section)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username", "is_staff", "is_performer", "display_factory"]

    def display_factory(self, obj):
        match obj.factories.all().count():
            case 0: return '-'
            case 1: return obj.factories.first()
            case _: return str(obj.factories.first()) + ', ...'

    display_factory.short_description = _("List of Factories")

    list_filter = ["is_staff", "is_performer", "factories"]
    fieldsets = (
        (None, {'fields': ('username', 'factories')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_superuser", "is_performer", "groups")},
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
         ),
    )
    search_fields = ['username']
    ordering = ['username']
    filter_horizontal = ()
    readonly_fields = [
        'created_at',
    ]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # Add change password button
        extra_context['Change Password'] = redirect('../password/').url

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


admin.site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    form = GroupChangeForm
    search_fields = ('name',)
    ordering = ('name',)


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.register(Attendance)