from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit

from accounts.models import Factory, User, Section
from repair_records.models import RepairType, Equipment
from .models import RepairRecord, EquipmentInactiveTime


class RepairRecordForm(forms.ModelForm):
    class Meta:
        model = RepairRecord
        fields = ('factory', 'section', 'equipment', 'performers', 'master', 'repair_type', 'start_time', 'end_time', 'reason', 'work_done', 'details_info')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(RepairRecordForm, self).__init__(*args, **kwargs)

        # CUSTOM GRIDING
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("factory"),  # Add classes for Bootstrap styling
            Div(
                Field("section"),  # Add classes for Bootstrap styling
                Field("equipment"),  # Add classes for Bootstrap styling
                css_class="row",  # Add classes for Bootstrap styling
            ),
            Field("performers"),  # Add classes for Bootstrap styling
            Div(
                Field("master"),  # Add classes for Bootstrap styling
                Field("repair_type"),  # Add classes for Bootstrap styling
                css_class="row",  # Add classes for Bootstrap styling
            ),
            Div(
                Field("start_time"),  # Add classes for Bootstrap styling
                Field("end_time"),  # Add classes for Bootstrap styling
                css_class="row",  # Add classes for Bootstrap styling
            ),
            Field("reason"),  # Add classes for Bootstrap styling
            Field("work_done"),  # Add classes for Bootstrap styling
            Field("details_info"),  # Add the details_info field here
            Div(
                # Add the Submit button
                Submit("submit", _("Submit"), css_class="btn btn-primary col-1"),
                css_class="form-group row justify-content-end",
            ),
        )

        if user.is_superuser:
            factories = Factory.objects.all()
        else:
            # Replace with the actual attribute that defines the factory
            factories = user.factories.all()
        sections = Section.objects.filter(factory__in=factories)
        perm = "add_repairrecord"
        perm_obj = Permission.objects.get(codename=perm)

        # FIELD: Factory
        if factories.count() == 1:
            # User is not an admin and is attached to only one factory
            # Set the factory to that value and hide the field
            self.fields["factory"].initial = factories.first()
            self.fields["factory"].widget = forms.HiddenInput()
        elif factories.count() > 1:
            # User is not an admin and is attached to multiple factories
            # Allow the user to select one of them
            self.fields["factory"].queryset = factories
        else:
            # User is not an admin but not attached to any factories
            # Handle this case as needed
            pass

        # FIELD: Section
        self.fields["section"].queryset = sections

        # FIELD: Master
        if user.is_superuser:
            # Allow admins to select any master
            self.fields["master"].queryset = User.objects.filter(
                Q(groups__permissions=perm_obj) | Q(user_permissions=perm_obj)
            )
        elif user.has_perm("repair_records.view_repairrecord"):
            # Filter "master" options based on the factory of the analyzer
            obj = User.objects.filter(
                Q(groups__permissions=perm_obj) | Q(user_permissions=perm_obj)
            )
            self.fields["master"].queryset = obj.filter(factories__in=factories)
        elif user.has_perm("repair_records.add_repairrecord"):
            # Hide "master" field for masters
            self.fields["master"].initial = user
            self.fields["master"].widget = forms.HiddenInput()

        # FIELD: Performers
        self.fields["performers"].required = False
        if user.is_superuser:
            # Allow admins to select any master
            self.fields["performers"].queryset = User.objects.filter(is_performer=True)
        elif user.has_perm("repair_records.view_repairrecord"):
            # Filter "performers" options based on the factory of the analyzer
            obj = User.objects.filter(is_performer=True)
            self.fields["performers"].queryset = obj.filter(factories__in=factories)
        elif user.has_perm("repair_records.add_repairrecord"):
            # Filter "performers" options based on the factory of the analyzer
            obj = User.objects.filter(is_performer=True)
            self.fields["performers"].queryset = obj.filter(factories__in=factories)

        # FIELD: Repair Type
        if not user.is_superuser:
            self.fields["repair_type"].queryset = RepairType.objects.filter(
                factory__in=factories
            )

        # FIELD: Equipment
        if not user.is_superuser:
            self.fields["equipment"].queryset = Equipment.objects.filter(
                section__in=sections
            )
            # FIELD: Details_Info
        if not user.is_superuser:
            self.fields["details_info"].queryset = Equipment.objects.filter(
                section__in=sections
            )

class MassUploadForm(forms.Form):
    ALLOWED_EXTENSIONS = [".xlsx", ".csv", ".xls"]

    file = forms.FileField(
        label=_("Select a file"),
        help_text=_("Only XLSX, CSV, and XLS files are allowed."),
    )

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith(tuple(self.ALLOWED_EXTENSIONS)):
            raise ValidationError(
                "File type not supported. Only XLSX, CSV, and XLS files are allowed."
            )
        return file


class EquipmentInactiveTimeForm(forms.ModelForm):
    class Meta:
        model = EquipmentInactiveTime
        fields = "__all__"
