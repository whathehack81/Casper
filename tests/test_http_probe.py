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
