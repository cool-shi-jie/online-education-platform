from django.utils import timezone
from rest_framework import decorators, exceptions, permissions, response, viewsets

from apps.courses.models import Enrollment
from .categories import COMMUNITY_POST_CATEGORIES
from .models import (
    CommunityPost,
    CommunityPostFavorite,
    CommunityPostLike,
    CommunityReply,
    CourseQuestion,
    ForumPost,
    ForumReply,
    LearningResource,
    LearningResourceFavorite,
)
from .preview import refresh_resource_preview
from .serializers import (
    CommunityPostSerializer,
    CommunityReplySerializer,
    CourseQuestionSerializer,
    ForumPostSerializer,
    ForumReplySerializer,
    LearningResourceSerializer,
)


def can_join_forum(user, course):
    if user.is_platform_admin or course.teacher_id == user.id:
        return True
    return Enrollment.objects.filter(student=user, course=course).exists()


class ForumPostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = ForumPost.objects.select_related("course", "author").filter(is_deleted=False)
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user) | queryset.filter(course__enrollments__student=user)
        return queryset.filter(course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not can_join_forum(self.request.user, course):
            raise exceptions.PermissionDenied("没有访问该课程论坛的权限。")
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_platform_admin or instance.author_id == user.id):
            raise exceptions.PermissionDenied("只能删除自己的帖子。")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    @decorators.action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        post = self.get_object()
        replies = post.replies.filter(is_deleted=False).select_related("author")
        page = self.paginate_queryset(replies)
        serializer = ForumReplySerializer(page or replies, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return response.Response(serializer.data)


class ForumReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ForumReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["post"]

    def get_queryset(self):
        user = self.request.user
        queryset = ForumReply.objects.select_related("post", "post__course", "author").filter(is_deleted=False)
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(post__course__teacher=user) | queryset.filter(post__course__enrollments__student=user)
        return queryset.filter(post__course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        post = serializer.validated_data["post"]
        if not can_join_forum(self.request.user, post.course):
            raise exceptions.PermissionDenied("没有回复该课程论坛的权限。")
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_platform_admin or instance.author_id == user.id):
            raise exceptions.PermissionDenied("只能删除自己的回复。")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


class CommunityPostViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["category"]
    search_fields = ["title", "content", "category"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        queryset = CommunityPost.objects.select_related("author").filter(is_deleted=False)
        if self.request.query_params.get("mine") == "true":
            return queryset.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(detail=False, methods=["get"])
    def categories(self, request):
        return response.Response(COMMUNITY_POST_CATEGORIES)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_platform_admin or instance.author_id == user.id):
            raise exceptions.PermissionDenied("只能删除自己的社区帖子。")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    @decorators.action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        post = self.get_object()
        replies = post.replies.filter(is_deleted=False).select_related("author")
        page = self.paginate_queryset(replies)
        serializer = CommunityReplySerializer(page or replies, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["post"])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        like = CommunityPostLike.objects.filter(post=post, user=request.user).first()
        if like:
            like.delete()
            liked = False
        else:
            CommunityPostLike.objects.create(post=post, user=request.user)
            liked = True
        return response.Response(
            {
                "liked": liked,
                "likes_count": post.likes.count(),
            }
        )

    @decorators.action(detail=True, methods=["post"])
    def toggle_favorite(self, request, pk=None):
        post = self.get_object()
        favorite = CommunityPostFavorite.objects.filter(post=post, user=request.user).first()
        if favorite:
            favorite.delete()
            favorited = False
        else:
            CommunityPostFavorite.objects.create(post=post, user=request.user)
            favorited = True
        return response.Response(
            {
                "favorited": favorited,
                "favorites_count": post.favorites.count(),
            }
        )

    @decorators.action(detail=False, methods=["get"])
    def favorites(self, request):
        queryset = (
            CommunityPost.objects.select_related("author")
            .filter(is_deleted=False, favorites__user=request.user)
            .order_by("-favorites__created_at")
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return response.Response(serializer.data)


class CommunityReplyViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["post"]

    def get_queryset(self):
        return CommunityReply.objects.select_related("post", "author").filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_platform_admin or instance.author_id == user.id):
            raise exceptions.PermissionDenied("只能删除自己的社区回复。")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


class LearningResourceViewSet(viewsets.ModelViewSet):
    serializer_class = LearningResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["category", "is_published"]
    search_fields = ["title", "summary", "category"]

    def get_queryset(self):
        queryset = LearningResource.objects.select_related("publisher")
        if self.request.query_params.get("mine") == "true":
            return queryset.filter(publisher=self.request.user)
        if self.request.user.is_teacher or self.request.user.is_platform_admin:
            return queryset
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        resource = serializer.save(publisher=self.request.user)
        if not resource.cover and resource.url:
            refresh_resource_preview(resource)

    def perform_update(self, serializer):
        if not (self.request.user.is_platform_admin or serializer.instance.publisher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己发布的学习资料。")
        resource = serializer.save()
        if not resource.cover and resource.url:
            refresh_resource_preview(resource, force=True)
        elif not resource.url:
            refresh_resource_preview(resource)

    def perform_destroy(self, instance):
        if not (self.request.user.is_platform_admin or instance.publisher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能删除自己发布的学习资料。")
        instance.delete()

    @decorators.action(detail=True, methods=["post"])
    def toggle_favorite(self, request, pk=None):
        resource = self.get_object()
        favorite = LearningResourceFavorite.objects.filter(resource=resource, user=request.user).first()
        if favorite:
            favorite.delete()
            favorited = False
        else:
            LearningResourceFavorite.objects.create(resource=resource, user=request.user)
            favorited = True
        return response.Response(
            {
                "favorited": favorited,
                "favorites_count": resource.favorites.count(),
            }
        )

    @decorators.action(detail=False, methods=["get"])
    def favorites(self, request):
        queryset = (
            LearningResource.objects.select_related("publisher")
            .filter(favorites__user=request.user)
            .order_by("-favorites__created_at")
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return response.Response(serializer.data)


class CourseQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = CourseQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "chapter", "status", "student"]
    search_fields = ["title", "content", "answer", "course__title", "chapter__title", "student__username"]
    ordering_fields = ["created_at", "updated_at", "answered_at", "resolved_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = CourseQuestion.objects.select_related("course", "chapter", "student", "answered_by")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user)
        return queryset.filter(student=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_teacher and not user.is_platform_admin:
            raise exceptions.PermissionDenied("教师不能以学生身份发起课程疑问。")
        course = serializer.validated_data["course"]
        if user.is_student and not Enrollment.objects.filter(student=user, course=course).exists():
            raise exceptions.PermissionDenied("只能对已报名课程发起疑问。")
        serializer.save(student=user, status=CourseQuestion.Status.PENDING)

    def perform_update(self, serializer):
        if not self.request.user.is_platform_admin:
            raise exceptions.PermissionDenied("不支持直接修改疑问，请使用回复或已解决操作。")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_platform_admin or instance.student_id == user.id):
            raise exceptions.PermissionDenied("只能删除自己的疑问。")
        instance.delete()

    @decorators.action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        question = self.get_object()
        user = request.user
        if not (user.is_platform_admin or question.course.teacher_id == user.id):
            raise exceptions.PermissionDenied("只能回复自己课程下的疑问。")
        answer = (request.data.get("answer") or "").strip()
        if not answer:
            raise exceptions.ValidationError({"answer": "回复内容不能为空。"})

        now = timezone.now()
        question.answer = answer
        question.answered_by = user
        question.answered_at = now
        if question.status != CourseQuestion.Status.RESOLVED:
            question.status = CourseQuestion.Status.ANSWERED
            question.resolved_at = None
            question.save(update_fields=["answer", "answered_by", "answered_at", "status", "resolved_at", "updated_at"])
        else:
            question.save(update_fields=["answer", "answered_by", "answered_at", "updated_at"])
        serializer = self.get_serializer(question)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        question = self.get_object()
        user = request.user
        if not (user.is_platform_admin or question.student_id == user.id):
            raise exceptions.PermissionDenied("只能将自己的疑问标记为已解决。")
        if question.status == CourseQuestion.Status.PENDING:
            raise exceptions.ValidationError({"status": "疑问尚未收到回复，不能标记为已解决。"})

        question.status = CourseQuestion.Status.RESOLVED
        question.resolved_at = timezone.now()
        question.save(update_fields=["status", "resolved_at", "updated_at"])
        serializer = self.get_serializer(question)
        return response.Response(serializer.data)