from django.urls import path

from abren_one.modules.beneficiaries.interfaces.api.v1.views import (
    BeneficiaryDetailView,
    BeneficiaryListCreateView,
    ServiceDeliveryDetailView,
    ServiceDeliveryListCreateView,
)

app_name = "beneficiaries_api_v1"

urlpatterns = [
    path("", BeneficiaryListCreateView.as_view(), name="beneficiary-list-create"),
    path("<uuid:beneficiary_id>/", BeneficiaryDetailView.as_view(), name="beneficiary-detail"),
    path("deliveries/", ServiceDeliveryListCreateView.as_view(), name="service-delivery-list-create"),
    path("deliveries/<uuid:delivery_id>/", ServiceDeliveryDetailView.as_view(), name="service-delivery-detail"),
]
