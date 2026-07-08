import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen


TITLE_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_PATTERN = re.compile(
    r"<meta[^>]+(?:property|name)=[\"'](?P<name>[^\"']+)[\"'][^>]+content=[\"'](?P<content>[^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)


def _fetch_page(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=8) as response:
        return response.read().decode("utf-8", errors="ignore")


def _extract_preview(html):
    site_name = ""
    image_url = ""
    for match in META_PATTERN.finditer(html):
        name = (match.group("name") or "").lower()
        content = (match.group("content") or "").strip()
        if not content:
            continue
        if name == "og:site_name" and not site_name:
            site_name = content
        elif name == "og:image" and not image_url:
            image_url = content
        elif name == "twitter:image" and not image_url:
            image_url = content
    if not site_name:
        title_match = TITLE_PATTERN.search(html)
        if title_match:
            site_name = re.sub(r"\s+", " ", title_match.group(1)).strip()
    return image_url, site_name


def refresh_resource_preview(resource, force=False):
    if not resource.url:
        resource.preview_image_url = ""
        resource.preview_site_name = ""
        resource.save(update_fields=["preview_image_url", "preview_site_name"])
        return resource
    if resource.cover and not force:
        return resource
    if resource.preview_image_url and resource.preview_site_name and not force:
        return resource

    try:
        html = _fetch_page(resource.url)
        image_url, site_name = _extract_preview(html)
    except Exception:
        image_url, site_name = "", ""

    if image_url:
        image_url = urljoin(resource.url, image_url)

    resource.preview_image_url = image_url
    resource.preview_site_name = site_name
    resource.save(update_fields=["preview_image_url", "preview_site_name"])
    return resource
