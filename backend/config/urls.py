"""Root URL configuration for Abren One."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from config.health import health, ready

urlpatterns = [
    path("health/", health, name="health"),
    path("ready/", ready, name="ready"),
    path("admin/", admin.site.urls),
    # OpenAPI Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Platform APIs
    path("api/v1/auth/", include("abren_one.platform.identity.interfaces.api.v1.urls")),
    # Business Module APIs
    path("api/v1/organizations/", include("abren_one.modules.organizations.interfaces.api.v1.urls")),
    path("api/v1/programs/", include("abren_one.modules.programs.interfaces.api.v1.urls")),
    path("api/v1/fundraising/", include("abren_one.modules.fundraising.interfaces.api.v1.urls")),
    path("api/v1/beneficiaries/", include("abren_one.modules.beneficiaries.interfaces.api.v1.urls")),
    path("api/v1/finance/", include("abren_one.modules.finance.interfaces.api.v1.urls")),
    path("api/v1/procurement/", include("abren_one.modules.procurement.interfaces.api.v1.urls")),
    path("api/v1/inventory/", include("abren_one.modules.inventory.interfaces.api.v1.urls")),
]

# Register Django Debug Toolbar if installed and in DEBUG mode
from django.conf import settings  # noqa: E402

if getattr(settings, "DEBUG", False):
    try:
        import debug_toolbar  # noqa: F401

        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
            *urlpatterns,
        ]
    except ImportError:
        pass
