from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from core.serializers.user import (
    RegisterSerializer,
    UserPublicSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


# ======================================
# 1) Đăng ký (Register)
# POST /api/user/register/
# ======================================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserPublicSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


# ======================================
# 2) Lấy thông tin user đang đăng nhập
# GET /api/user/me/
# ======================================
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    return Response(UserPublicSerializer(request.user).data)


# ======================================
# 3) Update thông tin tài khoản
# PUT /api/user/update/
# ======================================
@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def update_user(request):
    serializer = UserUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Cập nhật thành công"})


# ======================================
# 4) Đổi mật khẩu
# PUT /api/user/change-password/
# ======================================
@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"detail": "Đổi mật khẩu thành công"})
