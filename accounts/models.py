from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _

from config.settings import LANGUAGES
from .managers import Manager


class Factory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Name"), max_length=100, unique=True)
    equation = models.CharField(_("Equation"), max_length=200)
    shift_hours = models.PositiveIntegerField(
        _("Shift hours"),
        default=8,
        validators=[
            MaxValueValidator(24),
        ],
    )
    file = models.FileField(_("File"), upload_to="files/", blank=True)

    class Meta:
        db_table = "factories"
        verbose_name = _("Factory")
        verbose_name_plural = _("Factories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        print(self.equation)
        self.equation = self.equation.replace(",", ".")
        self.equation = self.equation.replace("\.", ",")
        print(self.equation)

        super().save(*args, **kwargs)


class Section(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    factory = models.ForeignKey(
        Factory, verbose_name=_("Factory"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(_("Username"), max_length=100, unique=True)
    first_name = models.CharField(
        _("First name"), max_length=100, null=True, blank=True
    )
    last_name = models.CharField(_("Last name"), max_length=150, null=True, blank=True)

    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    factories = models.ManyToManyField(Factory, blank=True, verbose_name=_("Factories"))
    preferred_language = models.CharField(max_length=5, choices=LANGUAGES, default="ru")
    is_performer = models.BooleanField(_("Is performer"), default=False)

    objects = Manager()
    email = None

    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    date = models.DateField(_("Date"))
    is_present = models.BooleanField(_("Is present"), default=True)
    shift_hours = models.FloatField(_("Shift hours"), default=8)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        db_table = "attendances"
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")

    def __str__(self):
        return f"{self.user} {self.date}"
