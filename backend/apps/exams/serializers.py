from rest_framework import serializers

from apps.courses.models import Enrollment
from .models import Choice, Exam, ExamSubmission, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "question", "content", "is_correct", "order"]
        read_only_fields = ["id"]
        extra_kwargs = {"is_correct": {"write_only": True}}


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "exam", "title", "question_type", "score", "order", "choices"]
        read_only_fields = ["id"]


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "is_published",
            "total_score",
            "pass_score",
            "excellent_score",
            "questions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        total_score = attrs.get("total_score", getattr(self.instance, "total_score", 100))
        pass_score = attrs.get("pass_score", getattr(self.instance, "pass_score", 60))
        excellent_score = attrs.get("excellent_score", getattr(self.instance, "excellent_score", 85))
        if pass_score > total_score:
            raise serializers.ValidationError("及格线不能高于总分。")
        if excellent_score > total_score:
            raise serializers.ValidationError("优秀线不能高于总分。")
        if excellent_score < pass_score:
            raise serializers.ValidationError("优秀线不能低于及格线。")
        return attrs


class ExamSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)

    class Meta:
        model = ExamSubmission
        fields = ["id", "student", "student_name", "exam", "exam_title", "answers", "score", "passed", "submitted_at"]
        read_only_fields = ["id", "student", "score", "passed", "submitted_at"]

    def validate(self, attrs):
        request = self.context["request"]
        exam = attrs["exam"]
        if not exam.is_published:
            raise serializers.ValidationError("考试尚未发布。")
        if ExamSubmission.objects.filter(student=request.user, exam=exam).exists():
            raise serializers.ValidationError("该考试已经提交，不能重复提交。")
        enrollment = Enrollment.objects.filter(student=request.user, course=exam.course).first()
        if not enrollment:
            raise serializers.ValidationError("请先报名课程。")
        if enrollment.progress_percent < 100:
            raise serializers.ValidationError("完成课程学习后才能参加考试。")
        return attrs


def calculate_score(exam, answers):
    score = 0
    for question in exam.questions.prefetch_related("choices"):
        correct_ids = set(question.choices.filter(is_correct=True).values_list("id", flat=True))
        raw_answer = answers.get(str(question.id), [])
        selected_ids = set(raw_answer if isinstance(raw_answer, list) else [raw_answer])
        selected_ids = {int(item) for item in selected_ids if str(item).isdigit()}
        if selected_ids == correct_ids:
            score += question.score
    return score
