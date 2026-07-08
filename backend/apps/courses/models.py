from django.conf import settings
from django.db import models

from apps.common.validators import validate_image, validate_material, validate_video


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        ARCHIVED = "archived", "已下架"

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teaching_courses")
    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.CharField(max_length=60)
    language = models.CharField(max_length=20, default="zh-CN")
    cover = models.ImageField(upload_to="course_covers/", validators=[validate_image], blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    pass_score = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    video = models.FileField(upload_to="videos/", validators=[validate_video], blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="materials", blank=True, null=True)
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to="materials/", validators=[validate_material])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    progress_percent = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-created_at"]


class ChapterProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="chapter_progress")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="progress_records")
    is_completed = models.BooleanField(default=False)
    watched_seconds = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("enrollment", "chapter")
