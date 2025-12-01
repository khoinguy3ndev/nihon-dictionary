from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.api.auth import forgot_password, reset_password, verify_reset_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view()),
    path("api/auth/token/refresh/", TokenRefreshView.as_view()),
    path("api/auth/forgot-password/", forgot_password),
    path("api/auth/reset-password/", reset_password),
    path("api/auth/verify-reset-token/", verify_reset_token),
    path("api/", include("core.api.urls")),
]