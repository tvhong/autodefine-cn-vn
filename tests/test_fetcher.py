"""Tests for fetcher module."""

import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.fetcher import fetch_audio, fetch_webpage, format_url


class TestFormatUrl:
    """Test suite for URL formatting function."""

    def test_format_url_with_simple_chinese_word(self):
        """Test URL formatting with a simple Chinese word."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = "你好"

        result = format_url(url_template, chinese_word)

        assert result == "http://2.vndic.net/index.php?word=%E4%BD%A0%E5%A5%BD&dict=cn_vi"

    def test_format_url_with_complex_chinese_phrase(self):
        """Test URL formatting with a complex Chinese phrase."""
        url_template = "http://2.vndic.net/index.php?word={}&dict=cn_vi"
        chinese_word = "我爱学习中文"

        result = format_url(url_template, chinese_word)

        assert (
            result
            == "http://2.vndic.net/index.php?word=%E6%88%91%E7%88%B1%E5%AD%A6%E4%B9%A0%E4%B8%AD%E6%96%87&dict=cn_vi"
        )

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

        assert result == "http://2.vndic.net/index.php?word=%E4%BD%A0%E5%A5%BD%EF%BC%81&dict=cn_vi"


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
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        url = "http://2.vndic.net/index.php?word=你好&dict=cn_vi"
        timeout = 10

        with pytest.raises(urllib.error.URLError):
            fetch_webpage(url, timeout)

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_http_error(self, mock_urlopen):
        """Test handling of HTTP errors (404, 500, etc.)."""
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

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_webpage_handles_malformed_utf8(self, mock_urlopen):
        """Test that fetch_webpage handles malformed UTF-8 sequences."""
        # Create content with invalid UTF-8 bytes (incomplete sequence)
        # This simulates the issue found with words like 斯 and 讨厌
        malformed_content = (
            b"<html><head><meta charset=utf-8><title>"
            b"\xe6\x96"  # Incomplete UTF-8 sequence (should be 3 bytes)
            b'</title></head><body><font color="#7F0000">[s\xc4\xab]</font>'
            b'<img src="img/dict/CB1FF077.png"><td>test</td></body></html>'
        )
        mock_response = MagicMock()
        mock_response.read.return_value = malformed_content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        url = "http://2.vndic.net/index.php?word=斯&dict=cn_vi"
        timeout = 10

        # Should not raise UnicodeDecodeError
        result = fetch_webpage(url, timeout)

        # Result should contain replacement characters for invalid bytes
        assert isinstance(result, str)
        assert "<html>" in result
        assert 'font color="#7F0000"' in result
        # Invalid bytes should be replaced with Unicode replacement character
        assert "\ufffd" in result or "�" in result


class TestFetchAudio:
    """Test suite for audio fetching function."""

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_audio_success(self, mock_urlopen):
        """Test successful audio fetching."""
        # Mock the response with fake MP3 data
        mock_audio_data = b"\xff\xfb\x90\x00"  # Fake MP3 header
        mock_response = MagicMock()
        mock_response.read.return_value = mock_audio_data
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        audio_url = "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"
        base_url = "http://2.vndic.net"
        timeout = 10

        result = fetch_audio(audio_url, base_url, timeout)

        assert result == mock_audio_data
        # Verify full URL was constructed correctly
        call_args = mock_urlopen.call_args
        assert call_args[0][0] == "http://2.vndic.net/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_audio_with_absolute_url(self, mock_urlopen):
        """Test fetching audio when URL is already absolute."""
        mock_audio_data = b"\xff\xfb\x90\x00"
        mock_response = MagicMock()
        mock_response.read.return_value = mock_audio_data
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        audio_url = "http://example.com/audio.mp3"
        base_url = "http://2.vndic.net"
        timeout = 10

        result = fetch_audio(audio_url, base_url, timeout)

        assert result == mock_audio_data
        # Verify absolute URL was used as-is
        call_args = mock_urlopen.call_args
        assert call_args[0][0] == "http://example.com/audio.mp3"

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_audio_timeout_error(self, mock_urlopen):
        """Test handling of timeout errors during audio fetch."""
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        audio_url = "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"
        base_url = "http://2.vndic.net"
        timeout = 10

        with pytest.raises(urllib.error.URLError):
            fetch_audio(audio_url, base_url, timeout)

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_audio_http_error(self, mock_urlopen):
        """Test handling of HTTP errors during audio fetch."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        audio_url = "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"
        base_url = "http://2.vndic.net"
        timeout = 10

        with pytest.raises(urllib.error.HTTPError):
            fetch_audio(audio_url, base_url, timeout)
