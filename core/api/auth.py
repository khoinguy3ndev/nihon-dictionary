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
 # 1) Register
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
# 2) Get current logged-in user info
# GET /api/user/me/
# ======================================
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    return Response(UserPublicSerializer(request.user).data)


# ======================================
# 3) Update user info
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
    return Response({"detail": "Update successful"})


# ======================================
# 4) Change password
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
    return Response({"detail": "Password changed successfully"})


# ======================================
# 5) Request password reset (Forgot Password)
# POST /api/auth/forgot-password/
# ======================================
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    user = User.objects.get(email=email)

    # Delete old unused tokens for this user
    PasswordResetToken.objects.filter(user=user, is_used=False).delete()

    # Create new token
    reset_token = PasswordResetToken.objects.create(user=user)

    # Create reset password link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

    # Send email
    try:
        send_mail(
            subject="[Nihon Dictionary] Password Reset",
            message=f"""
Hello {user.username},

You have requested to reset your password for your Nihon Dictionary account.

Please click the following link to reset your password:
{reset_link}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
Nihon Dictionary Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        return Response(
            {"detail": f"Could not send email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({"detail": "Password reset email has been sent."})


# ======================================
# 6) Confirm password reset
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
            {"detail": "Invalid token."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not reset_token.is_valid():
        return Response(
            {"detail": "Token has expired or has already been used."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Set new password
    user = reset_token.user
    user.set_password(new_password)
    user.save()

    # Mark token as used
    reset_token.is_used = True
    reset_token.save()

    return Response({"detail": "Password has been reset successfully."})


# ======================================
# 7) Verify if reset token is valid
# GET /api/auth/verify-reset-token/?token=xxx
# ======================================
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def verify_reset_token(request):
    token_str = request.query_params.get("token", "")

    if not token_str:
        return Response(
            {"valid": False, "detail": "Token was not provided."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"valid": False, "detail": "Invalid token."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not reset_token.is_valid():
        return Response(
            {"valid": False, "detail": "Token has expired or has already been used."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"valid": True, "email": reset_token.user.email})
