from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Equipment, EquipmentNode, EquipmentInactiveTime,
    RepairType, WorkType, WorkAction,
    RepairRecord
)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "section", "get_factory_name")

    def get_factory_name(self, obj):
        return obj.section.factory.name if obj.section and obj.section.factory else None
    get_factory_name.short_description = _("Factory")
admin.site.register(Equipment, EquipmentAdmin)

admin.site.register(EquipmentNode)
admin.site.register(EquipmentInactiveTime)


admin.site.register(RepairType)
admin.site.register(WorkType)
admin.site.register(WorkAction)


class RepairRecordAdmin(admin.ModelAdmin):
    readonly_fields = ("total_time",)

admin.site.register(RepairRecord, RepairRecordAdmin)