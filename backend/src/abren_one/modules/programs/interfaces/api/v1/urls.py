from django.urls import path

from abren_one.modules.programs.interfaces.api.v1.views import (
    ActivityDetailView,
    ActivityListCreateView,
    ProgramDetailView,
    ProgramListCreateView,
    ProjectDetailView,
    ProjectListCreateView,
)

app_name = "programs_api_v1"

urlpatterns = [
    path("", ProgramListCreateView.as_view(), name="program-list-create"),
    path("<uuid:program_id>/", ProgramDetailView.as_view(), name="program-detail"),
    path("projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path("projects/<uuid:project_id>/", ProjectDetailView.as_view(), name="project-detail"),
    path("activities/", ActivityListCreateView.as_view(), name="activity-list-create"),
    path("activities/<uuid:activity_id>/", ActivityDetailView.as_view(), name="activity-detail"),
]
