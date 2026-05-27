from unittest.mock import MagicMock, patch

from casper.tools.http_probe import probe_url


def test_probe_url_success():
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers.get.return_value = "text/html"

    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    with patch("casper.tools.http_probe.urlopen", return_value=mock_response):
        result = probe_url("https://example.com")

    assert result == {
        "url": "https://example.com",
        "ok": True,
        "status": 200,
        "content_type": "text/html",
        "error": None,
    }


def test_probe_url_http_error():
    from urllib.error import HTTPError
    from io import BytesIO

    error = HTTPError(
        url="https://example.com/admin",
        code=403,
        msg="Forbidden",
        hdrs={"content-type": "text/html"},
        fp=BytesIO(),
    )

    with patch("casper.tools.http_probe.urlopen", side_effect=error):
        result = probe_url("https://example.com/admin")

    assert result["ok"] is False
    assert result["status"] == 403
    assert result["content_type"] == "text/html"
    assert "Forbidden" in result["error"]


def test_probe_url_url_error():
    from urllib.error import URLError

    with patch("casper.tools.http_probe.urlopen", side_effect=URLError("timeout")):
        result = probe_url("https://example.invalid")

    assert result == {
        "url": "https://example.invalid",
        "ok": False,
        "status": None,
        "content_type": None,
        "error": "timeout",
    }
