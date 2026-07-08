import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import exceptions, generics, permissions, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminRole
from .models import EmailVerificationCode
from .serializers import (
    ChangePasswordSerializer,
    MeUpdateSerializer,
    RegisterSerializer,
    RoleTokenObtainPairSerializer,
    UserSerializer,
)


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class SendEmailCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        purpose = (request.data.get("purpose") or "register").strip()
        if purpose != "register":
            raise exceptions.ValidationError({"purpose": "当前仅支持注册验证码。"})
        if not email:
            raise exceptions.ValidationError({"email": "邮箱不能为空。"})

        now = timezone.now()
        cooldown_seconds = getattr(settings, "EMAIL_CODE_COOLDOWN_SECONDS", 60)
        daily_limit = getattr(settings, "EMAIL_CODE_DAILY_LIMIT", 20)
        expire_seconds = getattr(settings, "EMAIL_CODE_EXPIRE_SECONDS", 300)

        today_count = EmailVerificationCode.objects.filter(
            email=email,
            purpose=purpose,
            created_at__date=now.date(),
        ).count()
        if today_count >= daily_limit:
            raise exceptions.Throttled(detail="今日验证码发送次数已达上限，请明日再试。")

        latest = EmailVerificationCode.objects.filter(email=email, purpose=purpose).order_by("-created_at").first()
        if latest and (now - latest.created_at).total_seconds() < cooldown_seconds:
            raise exceptions.Throttled(detail=f"发送过于频繁，请 {cooldown_seconds} 秒后再试。")

        code = f"{random.randint(0, 999999):06d}"
        EmailVerificationCode.objects.create(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=now + timedelta(seconds=expire_seconds),
        )

        send_mail(
            subject="在线教育平台注册验证码",
            message=f"你的注册验证码是：{code}，{expire_seconds // 60}分钟内有效。",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"detail": "验证码已发送"}, status=status.HTTP_200_OK)


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = MeUpdateSerializer(instance=request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "密码已更新。"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["username", "email"]
    filterset_fields = ["role", "is_active"]
