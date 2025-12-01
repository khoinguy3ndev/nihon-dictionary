from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from core.serializers.user import (
    RegisterSerializer,
    UserPublicSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from core.models import PasswordResetToken

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


# ======================================
# 5) Yêu cầu reset mật khẩu (Forgot Password)
# POST /api/auth/forgot-password/
# ======================================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    user = User.objects.get(email=email)

    # Xóa các token cũ chưa dùng của user này
    PasswordResetToken.objects.filter(user=user, is_used=False).delete()

    # Tạo token mới
    reset_token = PasswordResetToken.objects.create(user=user)

    # Tạo link reset password
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

    # Gửi email
    try:
        send_mail(
            subject="[Nihon Dictionary] Đặt lại mật khẩu",
            message=f"""
Xin chào {user.username},

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Nihon Dictionary.

Vui lòng nhấp vào liên kết sau để đặt lại mật khẩu:
{reset_link}

Liên kết này sẽ hết hạn sau 1 giờ.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
Nihon Dictionary Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        return Response(
            {"detail": f"Không thể gửi email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({"detail": "Email đặt lại mật khẩu đã được gửi."})


# ======================================
# 6) Xác nhận reset mật khẩu
# POST /api/auth/reset-password/
# ======================================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token_str = serializer.validated_data["token"]
    new_password = serializer.validated_data["new_password"]

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"detail": "Token không hợp lệ."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not reset_token.is_valid():
        return Response(
            {"detail": "Token đã hết hạn hoặc đã được sử dụng."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Đặt mật khẩu mới
    user = reset_token.user
    user.set_password(new_password)
    user.save()

    # Đánh dấu token đã sử dụng
    reset_token.is_used = True
    reset_token.save()

    return Response({"detail": "Mật khẩu đã được đặt lại thành công."})


# ======================================
# 7) Kiểm tra token có hợp lệ không
# GET /api/auth/verify-reset-token/?token=xxx
# ======================================
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def verify_reset_token(request):
    token_str = request.query_params.get("token", "")

    if not token_str:
        return Response(
            {"valid": False, "detail": "Token không được cung cấp."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"valid": False, "detail": "Token không hợp lệ."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not reset_token.is_valid():
        return Response(
            {"valid": False, "detail": "Token đã hết hạn hoặc đã được sử dụng."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"valid": True, "email": reset_token.user.email})
