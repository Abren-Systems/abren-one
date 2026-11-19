"""Root URL configuration for Abren One."""

from django.contrib import admin
from django.urls import include, path

from config.health import health, ready

urlpatterns = [
    path("health/", health, name="health"),
    path("ready/", ready, name="ready"),
    path("admin/", admin.site.urls),
    path("api/v1/organizations/", include("abren_one.modules.organizations.interfaces.api.v1.urls")),
    path("api/v1/programs/", include("abren_one.modules.programs.interfaces.api.v1.urls")),
    path("api/v1/fundraising/", include("abren_one.modules.fundraising.interfaces.api.v1.urls")),
]
