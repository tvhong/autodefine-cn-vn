"""Tests for fetcher module."""

from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.fetcher import (
    fetch_audio,
    fetch_webpage,
    format_url,
    parse_dictionary_content,
)


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


class TestParseDictionaryContent:
    """Test suite for parsing dictionary content."""

    def test_parse_valid_dictionary_content(self):
        """Test parsing valid dictionary HTML with pinyin and Vietnamese definition."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>[gōngjīn]</FONT></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon">ki-lô-gam。国际公制重量或质量主单位，一公斤等于一千克，合二市斤。</TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "gōngjīn"
        assert (
            result["vietnamese"]
            == "ki-lô-gam。国际公制重量或质量主单位，一公斤等于一千克，合二市斤。"
        )
        assert result["audio_url"] == ""

    def test_parse_content_with_extra_whitespace(self):
        """Test parsing content with extra whitespace."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>  [nǐhǎo]  </FONT></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon">  xin chào  </TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐhǎo"
        assert result["vietnamese"] == "xin chào"

    def test_parse_content_missing_pinyin(self):
        """Test parsing content when pinyin is missing."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon">xin chào</TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == ""
        assert result["vietnamese"] == "xin chào"

    def test_parse_content_missing_vietnamese(self):
        """Test parsing content when Vietnamese definition is missing."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>[nǐhǎo]</FONT></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon"></TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐhǎo"
        assert result["vietnamese"] == ""

    def test_parse_content_missing_table(self):
        """Test parsing content when TABLE element is missing."""
        html_content = "<html><body>No table here</body></html>"

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == ""
        assert result["vietnamese"] == ""

    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        html_content = ""

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == ""
        assert result["vietnamese"] == ""

    def test_parse_real_dictionary_page(self):
        """Test parsing a real dictionary page HTML (公斤 = kilogram)."""
        # This is the actual HTML structure from vndic.net for the word 公斤
        from pathlib import Path

        asset_path = Path(__file__).parent / "assets" / "vndic_net_gongjin.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "gōngjīn"
        assert "ki-lô-gam" in result["vietnamese"]
        assert "国际公制重量或质量主单位" in result["vietnamese"]

    def test_parse_real_dictionary_page_nimen(self):
        """Test parsing a real dictionary page HTML (你们 = you plural)."""
        # This is the actual HTML structure from vndic.net for the word 你们
        from pathlib import Path

        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ·men"
        assert "các ông" in result["vietnamese"]
        assert "các bà" in result["vietnamese"]
        assert "代词" in result["vietnamese"]

    def test_parse_real_dictionary_page_ni(self):
        """Test parsing a real dictionary page HTML (你 = you)."""
        # This is the actual HTML structure from vndic.net for the word 你
        from pathlib import Path

        asset_path = Path(__file__).parent / "assets" / "vndic_net_ni.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ"
        assert "anh" in result["vietnamese"]
        assert "chị" in result["vietnamese"]
        assert "称对方(一个人)" in result["vietnamese"]

    def test_parse_audio_url_from_html(self):
        """Test parsing audio URL from soundManager.play() call."""
        html_content = """
        <span onclick="soundManager.play('/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&');" style="cursor:pointer;">
            <img src="/images/loa.png" border="0"/>
        </span>
        """

        result = parse_dictionary_content(html_content)

        assert result["audio_url"] == "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"

    def test_parse_audio_url_missing(self):
        """Test parsing when audio URL is missing."""
        html_content = "<html><body>No audio here</body></html>"

        result = parse_dictionary_content(html_content)

        assert result["audio_url"] == ""

    def test_parse_real_dictionary_page_with_audio(self):
        """Test parsing a real dictionary page HTML with audio URL (你们 = you plural)."""
        from pathlib import Path

        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ·men"
        assert "các ông" in result["vietnamese"]
        assert result["audio_url"] == "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"


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
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        audio_url = "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"
        base_url = "http://2.vndic.net"
        timeout = 10

        with pytest.raises(urllib.error.URLError):
            fetch_audio(audio_url, base_url, timeout)

    @patch("autodefine_cn_vn.fetcher.urllib.request.urlopen")
    def test_fetch_audio_http_error(self, mock_urlopen):
        """Test handling of HTTP errors during audio fetch."""
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        audio_url = "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"
        base_url = "http://2.vndic.net"
        timeout = 10

        with pytest.raises(urllib.error.HTTPError):
            fetch_audio(audio_url, base_url, timeout)
