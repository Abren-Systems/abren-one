from django.urls import path

from abren_one.platform.identity.interfaces.api.v1.views import (
    CsrfTokenView,
    CurrentUserView,
    LoginView,
    LogoutView,
)

app_name = "identity_api_v1"

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", CurrentUserView.as_view(), name="auth-me"),
    path("csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
]
