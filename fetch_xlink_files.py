
from __future__ import annotations

import os
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import List, Tuple, Optional


DEFAULT_URL = "http://10.61.171.61/"


class AnchorHrefCollector(HTMLParser):
    """Collects href values from anchor tags."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name and name.lower() == "href" and value:
                self.hrefs.append(value)


def normalize_root_url(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("@"):
        url = url[1:]
    if not url:
        url = DEFAULT_URL
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    return url


def detect_text_encoding(content_type: str | None) -> Optional[str]:
    if not content_type:
        return None
    parts = [p.strip() for p in content_type.split(";")]
    for p in parts:
        if p.lower().startswith("charset="):
            return p.split("=", 1)[1].strip() or None
    return None


def _fetch_text(url: str, timeout: float = 15.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; X-urls-min/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type")
        encoding = detect_text_encoding(content_type) or "utf-8"
        return resp.read().decode(encoding, errors="replace")


def _find_xlink_url(root_url: str, timeout: float) -> Optional[str]:
    # First try the direct, most common path
    direct = urllib.parse.urljoin(root_url, "X-urls")
    try:
        # Small HEAD isn’t universally supported; do a GET and rely on caller to fetch once more
        # For minimalism, we instead parse the directory listing to avoid double fetching
        pass
    except Exception:
        pass

    # Parse directory listing to find an anchor named exactly 'Xlink' (prefer case-sensitive)
    html = _fetch_text(root_url, timeout)
    parser = AnchorHrefCollector()
    parser.feed(html)

    for href in parser.hrefs:
        basename = os.path.basename(urllib.parse.urlparse(href).path) or href
        if basename == "Xlink":
            return urllib.parse.urljoin(root_url, href)
    for href in parser.hrefs:
        basename = os.path.basename(urllib.parse.urlparse(href).path) or href
        if basename.lower() == "xlink":
            return urllib.parse.urljoin(root_url, href)

    # Fallback: if directory didn’t have anchors, still try direct URL
    return direct


def get_xlink_list(root_url: str = DEFAULT_URL, timeout: float = 15.0) -> List[str]:
    """Return the 'Xlink' file contents from the server as a list of non-empty lines."""
    root_url = normalize_root_url(root_url)
    xlink_url = _find_xlink_url(root_url, timeout)
    text = _fetch_text(xlink_url, timeout)
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line]


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    try:
        items = get_xlink_list(url)
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(items)


