from django.urls import path

from abren_one.modules.organizations.interfaces.api.v1.views import (
    ActivateMemberView,
    BranchListCreateView,
    CurrentOrganizationDetailView,
    DepartmentDetailView,
    DepartmentListCreateView,
    MemberListCreateView,
    ProvisionOrganizationView,
    RevokeMemberView,
    SuspendMemberView,
)

app_name = "organizations_api_v1"

urlpatterns = [
    path("", ProvisionOrganizationView.as_view(), name="organization-provision"),
    path("current/", CurrentOrganizationDetailView.as_view(), name="organization-current"),
    path("branches/", BranchListCreateView.as_view(), name="branch-list-create"),
    path("departments/", DepartmentListCreateView.as_view(), name="department-list-create"),
    path("departments/<uuid:department_id>/", DepartmentDetailView.as_view(), name="department-detail"),
    path("members/", MemberListCreateView.as_view(), name="member-list-create"),
    path(
        "members/<uuid:membership_id>/activate/",
        ActivateMemberView.as_view(),
        name="member-activate",
    ),
    path(
        "members/<uuid:membership_id>/suspend/",
        SuspendMemberView.as_view(),
        name="member-suspend",
    ),
    path("members/<uuid:membership_id>/revoke/", RevokeMemberView.as_view(), name="member-revoke"),
]
