from __future__ import annotations

from urllib.request import Request, urlopen


def probe_url(url: str, timeout: int = 10) -> dict:
    request = Request(
        url,
        headers={"User-Agent": "Casper/0.1"},
        method="GET",
    )

    with urlopen(request, timeout=timeout) as response:
        return {
            "url": url,
            "status": response.status,
            "content_type": response.headers.get("content-type"),
        }
