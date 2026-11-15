from django.urls import path

from abren_one.modules.fundraising.interfaces.api.v1.views import (
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
    path("donations/", DonationListCreateView.as_view(), name="fundraising-donation-list-create"),
]
