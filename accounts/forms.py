from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Factory

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username").title(),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "is_staff", "factories")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two password fields didn’t match."))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password1"))

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    factories = forms.ModelMultipleChoiceField(
        queryset=Factory.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Factories", False),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Groups", False),
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("User Permissions", False),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "factories",
            "is_staff",
            "is_superuser",
            "is_performer",
            "groups",
            "user_permissions",
        )


class GroupChangeForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "permissions")

    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.exclude(
            content_type__app_label__in=[
                "auth",
                "admin",
                "sessions",
                "users",
                "contenttypes",
            ],
        )
        .exclude(content_type__model__in=["factory", "section"])
        .exclude(codename__in=["add_user", "delete_user", "change_user"]),
        widget=FilteredSelectMultiple(_("permissions"), False),
    )
