from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmailVerificationCode


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "avatar", "bio", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "avatar", "bio"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确。")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    verification_code = serializers.CharField(write_only=True, min_length=6, max_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "verification_code"]

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("管理员账号请由后台创建。")
        return value

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip().lower()
        code = (attrs.get("verification_code") or "").strip()
        record = (
            EmailVerificationCode.objects.filter(
                email=email,
                purpose="register",
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )
        if not record:
            raise serializers.ValidationError({"verification_code": "请先获取邮箱验证码。"})
        if record.expires_at <= timezone.now():
            raise serializers.ValidationError({"verification_code": "验证码已过期，请重新获取。"})
        if record.code != code:
            raise serializers.ValidationError({"verification_code": "验证码错误。"})
        attrs["email"] = email
        attrs["_verification_record"] = record
        return attrs

    def create(self, validated_data):
        validated_data.pop("verification_code", None)
        record = validated_data.pop("_verification_record", None)
        password = validated_data.pop("password")
        with transaction.atomic():
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            if record:
                record.is_used = True
                record.save(update_fields=["is_used"])
        return user


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data
