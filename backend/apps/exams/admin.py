from django.contrib import admin

from .models import Choice, Exam, ExamSubmission, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_published", "total_score", "created_at")
    list_filter = ("is_published", "course")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "exam", "question_type", "score", "order")
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("content", "question", "is_correct", "order")


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "score", "passed", "submitted_at")
    list_filter = ("passed", "exam")
