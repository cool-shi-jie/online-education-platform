import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, StreamingHttpResponse
from django.utils.http import http_date


def _file_iterator(path, start, length, chunk_size=8192):
    with path.open(\"rb\") as file:
        file.seek(start)
        remaining = length
        while remaining > 0:
            chunk = file.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def range_media_response(request, path):
    media_root = Path(settings.MEDIA_ROOT).resolve()
    file_path = (media_root / path).resolve()
    if media_root not in file_path.parents or not file_path.is_file():
        raise Http404(\"Media file not found\")

    file_size = file_path.stat().st_size
    content_type = mimetypes.guess_type(file_path.name)[0] or \"application/octet-stream\"
    range_header = request.headers.get(\"Range\", \"\")

    if range_header.startswith(\"bytes=\"):
        range_value = range_header.removeprefix(\"bytes=\").split(\",\", 1)[0]
        start_text, _, end_text = range_value.partition(\"-\")
        try:
            start = int(start_text) if start_text else 0
            end = int(end_text) if end_text else file_size - 1
        except ValueError:
            start, end = 0, file_size - 1
        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))
        length = end - start + 1
        response = StreamingHttpResponse(
            _file_iterator(file_path, start, length),
            status=206,
            content_type=content_type,
        )
        response[\"Content-Range\"] = f\"bytes {start}-{end}/{file_size}\"
        response[\"Content-Length\"] = str(length)
    else:
        response = FileResponse(file_path.open(\"rb\"), content_type=content_type)
        response[\"Content-Length\"] = str(file_size)

    response[\"Accept-Ranges\"] = \"bytes\"
    response[\"Last-Modified\"] = http_date(file_path.stat().st_mtime)
    return response
