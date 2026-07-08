from rest_framework import serializers

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ["id", "code", "student", "student_name", "course", "course_title", "exam_submission", "file", "issued_at"]
        read_only_fields = ["id", "code", "student", "course", "exam_submission", "issued_at"]
