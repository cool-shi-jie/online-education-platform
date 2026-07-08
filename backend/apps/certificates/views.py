from rest_framework import permissions, viewsets

from .models import Certificate
from .serializers import CertificateSerializer


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["student", "course"]
    search_fields = ["code", "student__username", "course__title"]

    def get_queryset(self):
        user = self.request.user
        queryset = Certificate.objects.select_related("student", "course", "exam_submission")
        if user.is_platform_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(course__teacher=user)
        return queryset.filter(student=user)
