from rest_framework import decorators, exceptions, permissions, response, status, viewsets

from apps.accounts.permissions import IsTeacherOwnerOrAdminReadOnly
from .models import Chapter, ChapterProgress, Course, CourseMaterial, Enrollment
from .serializers import (
    ChapterProgressSerializer,
    ChapterSerializer,
    CourseMaterialSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    refresh_enrollment_progress,
)


def can_access_course_content(user, course):
    if not user.is_authenticated:
        return False
    if user.is_platform_admin or course.teacher_id == user.id:
        return True
    return Enrollment.objects.filter(student=user, course=course).exists()


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTeacherOwnerOrAdminReadOnly]
    filterset_fields = ["status", "category", "language", "teacher"]
    search_fields = ["title", "description", "category"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.select_related("teacher").prefetch_related("chapters", "materials")
        if not user.is_authenticated:
            return queryset.filter(status=Course.Status.PUBLISHED)
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(teacher=user) | queryset.filter(status=Course.Status.PUBLISHED)
        return queryset.filter(status=Course.Status.PUBLISHED)

    def perform_create(self, serializer):
        if not (self.request.user.is_teacher or self.request.user.is_platform_admin):
            raise exceptions.PermissionDenied("只有教师可以创建课程。")
        serializer.save(teacher=self.request.user)

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def categories(self, request):
        categories = (
            Course.objects.filter(status=Course.Status.PUBLISHED)
            .exclude(category="")
            .order_by("category")
            .values_list("category", flat=True)
            .distinct()
        )
        return response.Response(list(categories))

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if course.status != Course.Status.PUBLISHED:
            return response.Response({"detail": "课程尚未发布。"}, status=status.HTTP_400_BAD_REQUEST)
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        return response.Response(EnrollmentSerializer(enrollment, context={"request": request}).data, status=201 if created else 200)

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def complete_chapter(self, request, pk=None):
        course = self.get_object()
        chapter_id = request.data.get("chapter")
        watched_seconds = float(request.data.get("watched_seconds", 0) or 0)
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        if not enrollment:
            return response.Response({"detail": "请先报名课程。"}, status=status.HTTP_403_FORBIDDEN)
        chapter = Chapter.objects.filter(id=chapter_id, course=course).first()
        if not chapter:
            return response.Response({"detail": "章节不存在。"}, status=status.HTTP_404_NOT_FOUND)
        if chapter.video:
            if chapter.duration_seconds and watched_seconds < max(chapter.duration_seconds - 2, 0):
                return response.Response({"detail": "请先完整观看章节视频。"}, status=status.HTTP_400_BAD_REQUEST)
            if not chapter.duration_seconds and watched_seconds <= 0:
                return response.Response({"detail": "请先完整观看章节视频。"}, status=status.HTTP_400_BAD_REQUEST)
        progress, _ = ChapterProgress.objects.update_or_create(
            enrollment=enrollment,
            chapter=chapter,
            defaults={
                "is_completed": True,
                "watched_seconds": watched_seconds or chapter.duration_seconds,
            },
        )
        refresh_enrollment_progress(enrollment)
        return response.Response(ChapterProgressSerializer(progress).data)

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def progress(self, request, pk=None):
        course = self.get_object()
        if request.user.is_teacher and course.teacher_id == request.user.id or request.user.is_platform_admin:
            enrollments = course.enrollments.select_related("student", "course").prefetch_related("chapter_progress")
            return response.Response(EnrollmentSerializer(enrollments, many=True, context={"request": request}).data)
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        if not enrollment:
            return response.Response({"detail": "请先报名课程。"}, status=status.HTTP_403_FORBIDDEN)
        return response.Response(EnrollmentSerializer(enrollment, context={"request": request}).data)

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def recommendations(self, request, pk=None):
        course = self.get_object()
        items = Course.objects.filter(status=Course.Status.PUBLISHED, category=course.category).exclude(id=course.id)[:6]
        return response.Response(CourseSerializer(items, many=True, context={"request": request}).data)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "student"]

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.select_related("student", "course").prefetch_related("chapter_progress")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user)
        return queryset.filter(student=user)


class ChapterViewSet(viewsets.ModelViewSet):
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Chapter.objects.select_related("course", "course__teacher")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user) | queryset.filter(course__status=Course.Status.PUBLISHED)
        return queryset.filter(course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的章节。")
        serializer.save()

    def perform_update(self, serializer):
        course = serializer.instance.course
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的章节。")
        serializer.save()


class CourseMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = CourseMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CourseMaterial.objects.select_related("course", "chapter")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user) | queryset.filter(course__enrollments__student=user)
        return queryset.filter(course__enrollments__student=user).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能上传自己课程的资料。")
        serializer.save()

    def perform_update(self, serializer):
        course = serializer.instance.course
        if not (self.request.user.is_platform_admin or course.teacher_id == self.request.user.id):
            raise exceptions.PermissionDenied("只能维护自己课程的资料。")
        serializer.save()
