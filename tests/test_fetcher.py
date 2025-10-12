"""Tests for fetcher module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.fetcher import fetch_webpage, format_url


class TestFormatUrl:
    """Test suite for URL formatting function."""

    def test_format_url_with_simple_chinese_word(self):
        """Test URL formatting with a simple Chinese word."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = "你好"

        result = format_url(url_template, chinese_word)

        assert result == "http://2.vndic.net/index.php?word=你好&dict=cn_vi"

    def test_format_url_with_complex_chinese_phrase(self):
        """Test URL formatting with a complex Chinese phrase."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = "我爱学习中文"

        result = format_url(url_template, chinese_word)

        assert result == "http://2.vndic.net/index.php?word=我爱学习中文&dict=cn_vi"

    def test_format_url_with_empty_string(self):
        """Test URL formatting with an empty string."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = ""

        result = format_url(url_template, chinese_word)

        assert result == "http://2.vndic.net/index.php?word=&dict=cn_vi"

    def test_format_url_with_special_characters(self):
        """Test URL formatting with special characters."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = "你好！"

        result = format_url(url_template, chinese_word)

        assert result == "http://2.vndic.net/index.php?word=你好！&dict=cn_vi"


class TestFetchWebpage:
    """Test suite for webpage fetching function."""

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_success(self, mock_urlopen):
        """Test successful webpage fetching."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html><body>Test content</body></html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 10

        result = fetch_webpage(url, timeout)

        assert result == "<html><body>Test content</body></html>"
        mock_urlopen.assert_called_once()

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_with_utf8_content(self, mock_urlopen):
        """Test fetching webpage with UTF-8 content."""
        # Mock the response with Vietnamese text
        vietnamese_html = "<html><body>Xin chào 你好</body></html>"
        mock_response = MagicMock()
        mock_response.read.return_value = vietnamese_html.encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 10

        result = fetch_webpage(url, timeout)

        assert result == vietnamese_html
        assert "Xin chào" in result
        assert "你好" in result

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_timeout_error(self, mock_urlopen):
        """Test handling of timeout errors."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 10

        with pytest.raises(urllib.error.URLError):
            fetch_webpage(url, timeout)

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_http_error(self, mock_urlopen):
        """Test handling of HTTP errors (404, 500, etc.)."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 10

        with pytest.raises(urllib.error.HTTPError):
            fetch_webpage(url, timeout)

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_uses_timeout(self, mock_urlopen):
        """Test that fetch_webpage passes timeout to urlopen."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html></html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 15

        fetch_webpage(url, timeout)

        # Verify timeout was passed to urlopen
        call_args = mock_urlopen.call_args
        assert call_args[1]["timeout"] == timeout
