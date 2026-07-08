from django.contrib import admin

from .models import Chapter, ChapterProgress, Course, CourseMaterial, Enrollment


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "category", "language", "status", "created_at")
    list_filter = ("status", "category", "language")
    search_fields = ("title", "description", "teacher__username")
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_required")


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "chapter", "created_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "progress_percent", "completed_at", "created_at")
    list_filter = ("course",)


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "chapter", "is_completed", "updated_at")
