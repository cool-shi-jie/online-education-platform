from django.conf import settings
from django.db import models


class Exam(models.Model):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    total_score = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    class Type(models.TextChoices):
        SINGLE = "single", "单选"
        MULTIPLE = "multiple", "多选"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    title = models.TextField()
    question_type = models.CharField(max_length=20, choices=Type.choices, default=Type.SINGLE)
    score = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    content = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]


class ExamSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_submissions")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="submissions")
    answers = models.JSONField(default=dict)
    score = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ["-submitted_at"]
