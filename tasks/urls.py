from django.urls import path

from .views import (
    DashboardView,
    AddTaskView,
    AddSelectionView,
    ListTasksView,
    AttendanceView,
    SummaryTasksView,
    DiscardSummaryTasksView,
    SummaryPDFTasksView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="tasks_dashboard"),
    path("add/", AddTaskView.as_view(), name="tasks_add"),
    path(
        "add/selection/<str:option_type>/",
        AddSelectionView.as_view(),
        name="tasks_add_selection",
    ),
    path("list/", ListTasksView.as_view(), name="list_tasks"),
    path("attendance/", AttendanceView.as_view(), name="tasks_attendance"),
    path("summary/", SummaryTasksView.as_view(), name="tasks_summary"),
    path(
        "summary/discard/",
        DiscardSummaryTasksView.as_view(),
        name="tasks_summary_discard",
    ),
    path(
        "summary/export-pdf/",
        SummaryPDFTasksView.as_view(),
        name="tasks_summary_export_pdf",
    ),
]