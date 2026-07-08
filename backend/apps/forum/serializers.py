from rest_framework import serializers

from .categories import COMMUNITY_POST_CATEGORIES
from .models import CommunityPost, CommunityReply, CourseQuestion, ForumPost, ForumReply, LearningResource


class ForumReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = ForumReply
        fields = ["id", "post", "author", "author_name", "content", "is_deleted", "created_at"]
        read_only_fields = ["id", "author", "is_deleted", "created_at"]


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    replies_count = serializers.IntegerField(source="replies.count", read_only=True)

    class Meta:
        model = ForumPost
        fields = ["id", "course", "course_title", "author", "author_name", "title", "content", "is_deleted", "replies_count", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "is_deleted", "created_at", "updated_at"]


class CommunityReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = CommunityReply
        fields = ["id", "post", "author", "author_name", "content", "is_deleted", "created_at"]
        read_only_fields = ["id", "author", "is_deleted", "created_at"]


class CommunityPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    replies_count = serializers.IntegerField(source="replies.count", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    favorites_count = serializers.IntegerField(source="favorites.count", read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    favorited_by_me = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = [
            "id",
            "author",
            "author_name",
            "title",
            "content",
            "category",
            "image",
            "is_deleted",
            "replies_count",
            "likes_count",
            "favorites_count",
            "liked_by_me",
            "favorited_by_me",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "is_deleted", "created_at", "updated_at"]

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()

    def get_favorited_by_me(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def validate_category(self, value):
        if value not in COMMUNITY_POST_CATEGORIES:
            raise serializers.ValidationError("请选择有效的交流帖分类。")
        return value


class LearningResourceSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source="publisher.username", read_only=True)
    favorites_count = serializers.IntegerField(source="favorites.count", read_only=True)
    favorited_by_me = serializers.SerializerMethodField()

    class Meta:
        model = LearningResource
        fields = [
            "id",
            "publisher",
            "publisher_name",
            "title",
            "summary",
            "url",
            "category",
            "cover",
            "attachment",
            "preview_image_url",
            "preview_site_name",
            "favorites_count",
            "favorited_by_me",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["id", "publisher", "preview_image_url", "preview_site_name", "created_at"]

    def validate(self, attrs):
        url = attrs.get("url", getattr(self.instance, "url", ""))
        attachment = attrs.get("attachment", getattr(self.instance, "attachment", None))
        if not url and not attachment:
            raise serializers.ValidationError("网页地址和附件至少需要填写一个。")
        return attrs

    def get_favorited_by_me(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()


class CourseQuestionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    chapter_title = serializers.CharField(source="chapter.title", read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)
    answered_by_name = serializers.CharField(source="answered_by.username", read_only=True)
    status_text = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = CourseQuestion
        fields = [
            "id",
            "course",
            "course_title",
            "chapter",
            "chapter_title",
            "student",
            "student_name",
            "title",
            "content",
            "answer",
            "answered_by",
            "answered_by_name",
            "answered_at",
            "status",
            "status_text",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "answer",
            "answered_by",
            "answered_at",
            "status",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
