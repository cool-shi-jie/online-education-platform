from rest_framework import exceptions, permissions, viewsets

from apps.certificates.services import issue_certificate_if_eligible
from .models import Choice, Exam, ExamSubmission, Question
from .serializers import ChoiceSerializer, ExamSerializer, ExamSubmissionSerializer, QuestionSerializer, calculate_score


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "is_published"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        user = self.request.user
        queryset = Exam.objects.select_related("course", "course__teacher").prefetch_related("questions__choices")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user)
        return queryset.filter(is_published=True, course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能为自己的课程创建考试。")
        serializer.save()

    def perform_update(self, serializer):
        course = serializer.instance.course
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的考试。")
        serializer.save()


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Question.objects.select_related("exam", "exam__course", "exam__course__teacher")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(exam__course__teacher=user)
        return queryset.filter(exam__is_published=True, exam__course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        exam = serializer.validated_data["exam"]
        if not (self.request.user.is_platform_admin or exam.course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的题目。")
        serializer.save()


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Choice.objects.select_related("question", "question__exam", "question__exam__course")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(question__exam__course__teacher=user)
        return queryset.filter(question__exam__is_published=True, question__exam__course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        question = serializer.validated_data["question"]
        if not (self.request.user.is_platform_admin or question.exam.course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的选项。")
        serializer.save()


class ExamSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["exam", "student", "passed"]

    def get_queryset(self):
        user = self.request.user
        queryset = ExamSubmission.objects.select_related("student", "exam", "exam__course")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(exam__course__teacher=user)
        return queryset.filter(student=user)

    def perform_create(self, serializer):
        exam = serializer.validated_data["exam"]
        score = calculate_score(exam, serializer.validated_data["answers"])
        passed = score >= exam.course.pass_score
        submission = serializer.save(student=self.request.user, score=score, passed=passed)
        issue_certificate_if_eligible(submission)
