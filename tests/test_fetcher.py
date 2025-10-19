"""Tests for fetcher module."""

import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from autodefine_cn_vn.fetcher import (
    fetch_audio,
    fetch_webpage,
    format_url,
    parse_dictionary_content,
    parse_sample_sentences,
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
        asset_path = Path(__file__).parent / "assets" / "vndic_net_gongjin.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "gōngjīn"
        assert "ki-lô-gam" in result["vietnamese"]
        assert "国际公制重量或质量主单位" in result["vietnamese"]

    def test_parse_real_dictionary_page_nimen(self):
        """Test parsing a real dictionary page HTML (你们 = you plural)."""
        # This is the actual HTML structure from vndic.net for the word 你们
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
        asset_path = Path(__file__).parent / "assets" / "vndic_net_ni.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ"
        assert "anh" in result["vietnamese"]
        assert "chị" in result["vietnamese"]
        assert "称对方(一个人)" in result["vietnamese"]

    def test_parse_multiple_definitions(self):
        """Test parsing dictionary content with multiple definitions."""
        # The word 你 has 2 definitions in the real HTML
        asset_path = Path(__file__).parent / "assets" / "vndic_net_ni.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        # Should contain both definitions
        vietnamese = result["vietnamese"]
        # First definition: anh; chị; ông; bà; mày (chỉ một người)
        assert "anh; chị; ông; bà; mày (chỉ một người)" in vietnamese
        # Second definition: ta; người ta
        assert "ta; người ta" in vietnamese
        # Both definitions should be separated (e.g., by newline)
        definitions = vietnamese.split("\n")
        assert len(definitions) >= 2, f"Expected at least 2 definitions, got {len(definitions)}"

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
        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ·men"
        assert "các ông" in result["vietnamese"]
        assert result["audio_url"] == "/mp3.php?id=E4BDA0E4BBAC&dir=390&lang=cn&"

    def test_parse_dictionary_content_with_sentences(self):
        """Test that parse_dictionary_content includes sample sentences."""
        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert "sentences" in result
        assert len(result["sentences"]) == 2
        assert "你们" in result["sentences"][0]["chinese"]
        assert "歇一会儿" in result["sentences"][0]["chinese"]
        assert "các anh nghỉ" in result["sentences"][0]["vietnamese"]

    def test_parse_dictionary_content_no_sentences(self):
        """Test parsing content with no sample sentences."""
        html_content = """
        <span class="thisword"><font color="#93698E">你好</font></span>
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>[nǐhǎo]</FONT></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon">xin chào</TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐhǎo"
        assert result["vietnamese"] == "xin chào"
        assert result["sentences"] == []

    def test_parse_dictionary_content_missing_chinese_word(self):
        """Test parsing when Chinese word cannot be extracted."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>[nǐhǎo]</FONT></TD></TR>
        <TR><TD class="tacon"> </TD><TD class="tacon"><IMG src=img/dict/CB1FF077.png></TD>
        <TD class="tacon">xin chào</TD></TR></TABLE>
        """

        result = parse_dictionary_content(html_content)

        # Should still parse other fields, but sentences will be empty
        assert result["pinyin"] == "nǐhǎo"
        assert result["vietnamese"] == "xin chào"
        assert result["sentences"] == []


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


class TestParseSampleSentences:
    """Test suite for parsing sample sentences."""

    def test_parse_sample_sentences_with_two_sentences(self):
        """Test parsing multiple sample sentences from real HTML."""
        html_content = """
        <TR><TD class="tacon" colspan=2> </TD><TD class="tacon"><IMG src=img/dict/72B02D27.png></TD>
        <TD class="tacon"><FONT color=#FF0000>你们歇一会儿，让我们接着干。</FONT></TD></TR>
        <TR><TD class="tacon" colspan=3 width=54> </TD>
        <TD class="tacon"><FONT COLOR=#7F7F7F>các anh nghỉ một lát, để chúng tôi làm tiếp.</FONT></TD></TR>
        <TR><TD class="tacon" colspan=2> </TD><TD class="tacon"><IMG src=img/dict/72B02D27.png></TD>
        <TD class="tacon"><FONT color=#FF0000>你们弟兄中间谁是老大?</FONT></TD></TR>
        <TR><TD class="tacon" colspan=3 width=54> </TD>
        <TD class="tacon"><FONT COLOR=#7F7F7F>trong anh em các anh, ai là anh cả?</FONT></TD></TR>
        """

        result = parse_sample_sentences(html_content)

        assert len(result) == 2
        assert result[0]["chinese"] == "你们歇一会儿，让我们接着干。"
        assert result[0]["vietnamese"] == "các anh nghỉ một lát, để chúng tôi làm tiếp."
        assert result[1]["chinese"] == "你们弟兄中间谁是老大?"
        assert result[1]["vietnamese"] == "trong anh em các anh, ai là anh cả?"

    def test_parse_sample_sentences_no_sentences(self):
        """Test parsing when there are no sample sentences."""
        html_content = """
        <TABLE><TR><TD class="tacon"><IMG src=img/dict/02C013DD.png></TD>
        <TD class="tacon" colspan=2><FONT COLOR=#7F0000>[nǐhǎo]</FONT></TD></TR></TABLE>
        """

        result = parse_sample_sentences(html_content)

        assert result == []

    def test_parse_sample_sentences_basic(self):
        """Test parsing a basic sample sentence."""
        html_content = """
        <TR><TD class="tacon" colspan=2> </TD><TD class="tacon"><IMG src=img/dict/72B02D27.png></TD>
        <TD class="tacon"><FONT color=#FF0000>我爱你。</FONT></TD></TR>
        <TR><TD class="tacon" colspan=3 width=54> </TD>
        <TD class="tacon"><FONT COLOR=#7F7F7F>Tôi yêu bạn.</FONT></TD></TR>
        """

        result = parse_sample_sentences(html_content)

        assert len(result) == 1
        assert result[0]["chinese"] == "我爱你。"
        assert result[0]["vietnamese"] == "Tôi yêu bạn."

    def test_parse_sample_sentences_word_appears_multiple_times(self):
        """Test parsing when Chinese word appears multiple times in sentence."""
        html_content = """
        <TR><TD class="tacon" colspan=2> </TD><TD class="tacon"><IMG src=img/dict/72B02D27.png></TD>
        <TD class="tacon"><FONT color=#FF0000>你好吗？你呢？</FONT></TD></TR>
        <TR><TD class="tacon" colspan=3 width=54> </TD>
        <TD class="tacon"><FONT COLOR=#7F7F7F>Bạn khỏe không? Còn bạn?</FONT></TD></TR>
        """

        result = parse_sample_sentences(html_content)

        assert len(result) == 1
        assert result[0]["chinese"] == "你好吗？你呢？"

    def test_parse_sample_sentences_with_extra_whitespace(self):
        """Test parsing sentences with extra whitespace."""
        html_content = """
        <TR><TD class="tacon" colspan=2> </TD><TD class="tacon"><IMG src=img/dict/72B02D27.png></TD>
        <TD class="tacon"><FONT color=#FF0000>  你好  </FONT></TD></TR>
        <TR><TD class="tacon" colspan=3 width=54> </TD>
        <TD class="tacon"><FONT COLOR=#7F7F7F>  Xin chào  </FONT></TD></TR>
        """

        result = parse_sample_sentences(html_content)

        assert len(result) == 1
        # Whitespace should be stripped
        assert result[0]["chinese"] == "你好"
        assert result[0]["vietnamese"] == "Xin chào"

    def test_parse_sample_sentences_from_real_nimen_html(self):
        """Test parsing sample sentences from real vndic.net HTML (你们 = you plural)."""
        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_sample_sentences(html_content)

        assert len(result) == 2
        assert "你们" in result[0]["chinese"]
        assert "歇一会儿" in result[0]["chinese"]
        assert "các anh nghỉ" in result[0]["vietnamese"]
        assert "你们" in result[1]["chinese"]
        assert "弟兄中间" in result[1]["chinese"]
        assert "trong anh em" in result[1]["vietnamese"]
