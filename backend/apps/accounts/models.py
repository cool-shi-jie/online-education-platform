from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.validators import validate_image


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "学生"
        TEACHER = "teacher", "教师"
        ADMIN = "admin", "管理员"

    class Status(models.TextChoices):
        HAPPY = "happy", "开心"
        COOL = "cool", "冷漠"
        LEARNING = "learning", "学习中"
        BUSY = "busy", "忙碌"
        RESTING = "resting", "休息中"
        CHARGING = "charging", "充电中"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEARNING)
    avatar = models.ImageField(upload_to="avatars/", validators=[validate_image], blank=True, null=True)
    bio = models.TextField(blank=True)

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)


class EmailVerificationCode(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, default="login")
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
