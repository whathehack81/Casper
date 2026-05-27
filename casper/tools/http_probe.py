from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def probe_url(url: str, timeout: int = 10) -> dict:
    request = Request(
        url,
        headers={"User-Agent": "Casper/0.1"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "url": url,
                "ok": True,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
                "error": None,
            }
    except HTTPError as error:
        return {
            "url": url,
            "ok": False,
            "status": error.code,
            "content_type": error.headers.get("content-type"),
            "error": str(error),
        }
    except URLError as error:
        return {
            "url": url,
            "ok": False,
            "status": None,
            "content_type": None,
            "error": str(error.reason),
        }
