from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "student", "course", "issued_at")
    search_fields = ("code", "student__username", "course__title")
