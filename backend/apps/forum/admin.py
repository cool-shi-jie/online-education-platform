from django.contrib import admin

from .models import CourseQuestion, ForumPost, ForumReply


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "author", "is_deleted", "created_at")
    list_filter = ("is_deleted", "course")
    search_fields = ("title", "content", "author__username")


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_deleted", "created_at")
    list_filter = ("is_deleted",)


@admin.register(CourseQuestion)
class CourseQuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "chapter", "student", "status", "answered_by", "answered_at", "resolved_at", "created_at")
    list_filter = ("status", "course")
    search_fields = ("title", "content", "answer", "student__username", "course__title", "chapter__title")
