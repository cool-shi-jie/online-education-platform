from django.conf import settings
from django.db import models

from apps.common.validators import validate_image, validate_material


class ForumPost(models.Model):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="forum_posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_posts")
    title = models.CharField(max_length=160)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_replies")
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class CommunityPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=160)
    content = models.TextField()
    category = models.CharField(max_length=60, default="学习交流")
    image = models.ImageField(upload_to="community_posts/", validators=[validate_image], blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class CommunityPostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ["-created_at"]


class CommunityPostFavorite(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_post_favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")
        ordering = ["-created_at"]


class CommunityReply(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_replies")
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class LearningResource(models.Model):
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_resources")
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    url = models.URLField(blank=True)
    category = models.CharField(max_length=60, default="学习资料")
    cover = models.ImageField(upload_to="learning_resources/", validators=[validate_image], blank=True, null=True)
    attachment = models.FileField(upload_to="learning_resource_attachments/", validators=[validate_material], blank=True, null=True)
    preview_image_url = models.URLField(max_length=500, blank=True)
    preview_site_name = models.CharField(max_length=120, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class LearningResourceFavorite(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_resource_favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("resource", "user")
        ordering = ["-created_at"]


class CourseQuestion(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待回复"
        ANSWERED = "answered", "已回复"
        RESOLVED = "resolved", "已解决"

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="questions")
    chapter = models.ForeignKey("courses.Chapter", on_delete=models.SET_NULL, related_name="questions", blank=True, null=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_questions")
    title = models.CharField(max_length=160)
    content = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="answered_course_questions", blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
