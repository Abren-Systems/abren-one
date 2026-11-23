from django.urls import path

from abren_one.modules.fundraising.interfaces.api.v1.views import (
    ActivateGrantView,
    AwardGrantView,
    CloseGrantView,
    DonationListCreateView,
    DonorDetailView,
    DonorListCreateView,
    GrantDetailView,
    GrantListCreateView,
)

urlpatterns = [
    path("donors/", DonorListCreateView.as_view(), name="fundraising-donor-list-create"),
    path("donors/<uuid:donor_id>/", DonorDetailView.as_view(), name="fundraising-donor-detail"),
    path("grants/", GrantListCreateView.as_view(), name="fundraising-grant-list-create"),
    path("grants/<uuid:grant_id>/", GrantDetailView.as_view(), name="fundraising-grant-detail"),
    path("grants/<uuid:grant_id>/award/", AwardGrantView.as_view(), name="fundraising-grant-award"),
    path("grants/<uuid:grant_id>/activate/", ActivateGrantView.as_view(), name="fundraising-grant-activate"),
    path("grants/<uuid:grant_id>/close/", CloseGrantView.as_view(), name="fundraising-grant-close"),
    path("donations/", DonationListCreateView.as_view(), name="fundraising-donation-list-create"),
]
