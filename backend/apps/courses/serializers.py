from django.utils import timezone
from rest_framework import serializers

from .models import Chapter, ChapterProgress, Course, CourseMaterial, Enrollment


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ["id", "course", "chapter", "title", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChapterSerializer(serializers.ModelSerializer):
    materials = CourseMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ["id", "course", "title", "description", "order", "video", "duration_seconds", "is_required", "materials"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        can_access = bool(
            user
            and user.is_authenticated
            and (
                user.is_platform_admin
                or instance.course.teacher_id == user.id
                or Enrollment.objects.filter(student=user, course=instance.course).exists()
            )
        )
        if not can_access:
            data["video"] = None
            data["materials"] = []
        return data


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    enrolled_count = serializers.IntegerField(source="enrollments.count", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "title",
            "description",
            "category",
            "language",
            "cover",
            "status",
            "pass_score",
            "chapters",
            "enrolled_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]


class ChapterProgressSerializer(serializers.ModelSerializer):
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)

    class Meta:
        model = ChapterProgress
        fields = ["id", "chapter", "chapter_title", "is_completed", "watched_seconds", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)
    chapter_progress = ChapterProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "course",
            "course_title",
            "progress_percent",
            "completed_at",
            "chapter_progress",
            "created_at",
        ]
        read_only_fields = ["id", "student", "progress_percent", "completed_at", "created_at"]


def refresh_enrollment_progress(enrollment):
    required = enrollment.course.chapters.filter(is_required=True)
    total = required.count()
    if total == 0:
        enrollment.progress_percent = 100
    else:
        completed = enrollment.chapter_progress.filter(chapter__is_required=True, is_completed=True).count()
        enrollment.progress_percent = round(completed * 100 / total)
    enrollment.completed_at = timezone.now() if enrollment.progress_percent >= 100 else None
    enrollment.save(update_fields=["progress_percent", "completed_at"])
    return enrollment
