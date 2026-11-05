from django.urls import path

from abren_one.modules.programs.interfaces.api.v1.views import (
    ProgramDetailView,
    ProgramListCreateView,
)

app_name = "programs_api_v1"

urlpatterns = [
    path("", ProgramListCreateView.as_view(), name="program-list-create"),
    path("<uuid:program_id>/", ProgramDetailView.as_view(), name="program-detail"),
]
