"""Root URL configuration for Abren One."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/organizations/", include("abren_one.modules.organizations.interfaces.api.v1.urls")),
    path("api/v1/programs/", include("abren_one.modules.programs.interfaces.api.v1.urls")),
    path("api/v1/fundraising/", include("abren_one.modules.fundraising.interfaces.api.v1.urls")),
]
