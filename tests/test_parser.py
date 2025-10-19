"""Tests for parser module."""

from pathlib import Path

from autodefine_cn_vn.parser import parse_dictionary_content, parse_sample_sentences


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
        assert result["vietnamese"] == [
            "ki-lô-gam。国际公制重量或质量主单位，一公斤等于一千克，合二市斤。"
        ]
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
        assert result["vietnamese"] == ["xin chào"]

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
        assert result["vietnamese"] == ["xin chào"]

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
        assert result["vietnamese"] == []

    def test_parse_content_missing_table(self):
        """Test parsing content when TABLE element is missing."""
        html_content = "<html><body>No table here</body></html>"

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == ""
        assert result["vietnamese"] == []

    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        html_content = ""

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == ""
        assert result["vietnamese"] == []

    def test_parse_real_dictionary_page(self):
        """Test parsing a real dictionary page HTML (公斤 = kilogram)."""
        # This is the actual HTML structure from vndic.net for the word 公斤
        asset_path = Path(__file__).parent / "assets" / "vndic_net_gongjin.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "gōngjīn"
        vietnamese_text = " ".join(result["vietnamese"])
        assert "ki-lô-gam" in vietnamese_text
        assert "国际公制重量或质量主单位" in vietnamese_text

    def test_parse_real_dictionary_page_nimen(self):
        """Test parsing a real dictionary page HTML (你们 = you plural)."""
        # This is the actual HTML structure from vndic.net for the word 你们
        asset_path = Path(__file__).parent / "assets" / "vndic_net_nimen.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ·men"
        vietnamese_text = " ".join(result["vietnamese"])
        assert "các ông" in vietnamese_text
        assert "các bà" in vietnamese_text
        assert "代词" in vietnamese_text

    def test_parse_real_dictionary_page_ni(self):
        """Test parsing a real dictionary page HTML (你 = you)."""
        # This is the actual HTML structure from vndic.net for the word 你
        asset_path = Path(__file__).parent / "assets" / "vndic_net_ni.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        assert result["pinyin"] == "nǐ"
        vietnamese_text = " ".join(result["vietnamese"])
        assert "anh" in vietnamese_text
        assert "chị" in vietnamese_text
        assert "称对方(一个人)" in vietnamese_text

    def test_parse_multiple_definitions(self):
        """Test parsing dictionary content with multiple definitions."""
        # The word 你 has 2 definitions in the real HTML
        asset_path = Path(__file__).parent / "assets" / "vndic_net_ni.html"
        html_content = asset_path.read_text(encoding="utf-8")

        result = parse_dictionary_content(html_content)

        # Should contain both definitions as separate list items
        vietnamese = result["vietnamese"]
        vietnamese_text = " ".join(vietnamese)
        # First definition: anh; chị; ông; bà; mày (chỉ một người)
        assert "anh; chị; ông; bà; mày (chỉ một người)" in vietnamese_text
        # Second definition: ta; người ta
        assert "ta; người ta" in vietnamese_text
        # Should have multiple definitions in the list
        assert len(vietnamese) >= 2, f"Expected at least 2 definitions, got {len(vietnamese)}"

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
        vietnamese_text = " ".join(result["vietnamese"])
        assert "các ông" in vietnamese_text
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
        assert result["vietnamese"] == ["xin chào"]
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
        assert result["vietnamese"] == ["xin chào"]
        assert result["sentences"] == []


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
