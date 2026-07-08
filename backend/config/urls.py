from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import ChangePasswordView, MeView, RegisterView, SendEmailCodeView, UserViewSet, RoleTokenObtainPairView
from apps.certificates.views import CertificateViewSet
from apps.courses.views import ChapterViewSet, CourseMaterialViewSet, CourseViewSet, EnrollmentViewSet
from apps.exams.views import ChoiceViewSet, ExamSubmissionViewSet, ExamViewSet, QuestionViewSet
from apps.forum.views import (
    CommunityPostViewSet,
    CommunityReplyViewSet,
    CourseQuestionViewSet,
    ForumPostViewSet,
    ForumReplyViewSet,
    LearningResourceViewSet,
)


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("courses", CourseViewSet, basename="course")
router.register("chapters", ChapterViewSet, basename="chapter")
router.register("materials", CourseMaterialViewSet, basename="material")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("exams", ExamViewSet, basename="exam")
router.register("questions", QuestionViewSet, basename="question")
router.register("choices", ChoiceViewSet, basename="choice")
router.register("submissions", ExamSubmissionViewSet, basename="submission")
router.register("forum/posts", ForumPostViewSet, basename="forum-post")
router.register("forum/replies", ForumReplyViewSet, basename="forum-reply")
router.register("community/posts", CommunityPostViewSet, basename="community-post")
router.register("community/replies", CommunityReplyViewSet, basename="community-reply")
router.register("community/resources", LearningResourceViewSet, basename="learning-resource")
router.register("course-questions", CourseQuestionViewSet, basename="course-question")
router.register("forum/questions", CourseQuestionViewSet, basename="course-question-legacy")
router.register("certificates", CertificateViewSet, basename="certificate")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", RoleTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/email-code/send/", SendEmailCodeView.as_view(), name="send_email_code"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
