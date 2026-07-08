import uuid

from django.conf import settings
from django.db import models

from apps.common.validators import validate_certificate


def generate_certificate_code():
    return uuid.uuid4().hex[:16].upper()


class Certificate(models.Model):
    code = models.CharField(max_length=40, unique=True, default=generate_certificate_code)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="certificates")
    exam_submission = models.OneToOneField("exams.ExamSubmission", on_delete=models.CASCADE, related_name="certificate")
    file = models.FileField(upload_to="certificates/", validators=[validate_certificate], blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.student} - {self.course}"
