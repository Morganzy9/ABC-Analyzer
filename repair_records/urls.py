from django.urls import path

from .views import (
    ListRepairRecordView,
    ListExcelRepairRecordView,
    AddRepairRecordView,
    AddSelectionView,
    SummaryRepairRecordView,
    SummaryCSVRepairRecordView,
    SummaryPDFRepairRecordView,
    GetRepairRecordView,
    MassUploadView,
    EquipmentView,
    EquipmentInactiveTimeView,
    ListUserView,
    ListCSVUserView,
    UserView,
)

urlpatterns = [
    path("list/", ListRepairRecordView.as_view(), name="list_repair_record"),
    path("repair-records/excel/", ListExcelRepairRecordView.as_view(), name="list_excel_repair_record"),
    path("summary/", SummaryRepairRecordView.as_view(), name="summary_repair_record"),
    path(
        "summary-csv/",
        SummaryCSVRepairRecordView.as_view(),
        name="summary_csv_repair_record",
    ),
    path(
        "summary-pdf/<int:factory_id>/",
        SummaryPDFRepairRecordView.as_view(),
        name="summary_pdf_repair_record",
    ),
    path("add/", AddRepairRecordView.as_view(), name="add_repair_record"),
    path(
        "add/selection/<str:option_type>/",
        AddSelectionView.as_view(),
        name="add_selection",
    ),
    path("get-info/<int:id>/", GetRepairRecordView.as_view(), name="get_repair_record_info"),
    path("upload/", MassUploadView.as_view(), name="mass_upload_repair_record"),
    path(
        "equipment/<int:id>/", EquipmentView.as_view(), name="equipment_repair_record"
    ),
    path(
        "equipment_time/",
        EquipmentInactiveTimeView.as_view(),
        name="equipment_time_repair_record",
    ),
    path("list-user", ListUserView.as_view(), name="list_user"),
    path("list-csv-user", ListCSVUserView.as_view(), name="list_csv_user"),
    path("user/<int:id>/", UserView.as_view(), name="user_repair_record"),
]
