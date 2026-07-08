from pathlib import Path

from django.core.exceptions import ValidationError


def validate_file(file, allowed_extensions, max_mb):
    extension = Path(file.name).suffix.lower()
    if extension not in allowed_extensions:
        raise ValidationError(f"仅支持以下文件类型：{', '.join(allowed_extensions)}")
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"文件大小不能超过 {max_mb}MB。")


def validate_image(file):
    validate_file(file, {".jpg", ".jpeg", ".png", ".webp"}, 5)


def validate_video(file):
    validate_file(file, {".mp4", ".webm", ".mov"}, 200)


def validate_material(file):
    validate_file(file, {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".zip"}, 50)


def validate_certificate(file):
    validate_file(file, {".pdf", ".png", ".jpg", ".jpeg"}, 10)
