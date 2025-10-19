"""Functions for parsing Chinese-Vietnamese dictionary HTML content."""

from typing import TypedDict

from bs4 import BeautifulSoup


class SampleSentence(TypedDict):
    """Structure for a sample sentence with Chinese and Vietnamese translations."""

    chinese: str
    vietnamese: str


class DictionaryContent(TypedDict):
    """Structure for parsed dictionary content."""

    pinyin: str
    vietnamese: list[str]
    audio_url: str
    sentences: list[SampleSentence]


def parse_dictionary_content(html_content: str) -> DictionaryContent:
    """Parse pinyin, Vietnamese definition, audio URL, and sample sentences from dictionary HTML content.

    Args:
        html_content: The HTML content to parse

    Returns:
        Dictionary with 'pinyin', 'vietnamese', 'audio_url', and 'sentences' keys.
        Returns empty strings for missing data, empty list for no sentences.

    Examples:
        >>> html = '<FONT COLOR=#7F0000>[gōngjīn]</FONT>'
        >>> result = parse_dictionary_content(html)
        >>> result['pinyin']
        'gōngjīn'
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract pinyin from <FONT COLOR=#7F0000> tag
    pinyin = ""
    font_tag = soup.find("font", {"color": "#7F0000"})
    if font_tag:
        pinyin = font_tag.get_text(strip=True)
        # Remove square brackets if present
        if pinyin.startswith("[") and pinyin.endswith("]"):
            pinyin = pinyin[1:-1]

    # Extract all Vietnamese definitions by finding all TDs after marker images
    vietnamese_definitions = []
    # Find all img tags with the specific marker image
    marker_imgs = soup.find_all("img", src=lambda x: bool(x) and "img/dict/CB1FF077.png" in x)
    for marker_img in marker_imgs:
        # Find the parent TD of the marker image
        marker_td = marker_img.find_parent("td")
        if marker_td:
            # Get the next sibling TD which contains the Vietnamese definition
            next_td = marker_td.find_next_sibling("td")
            if next_td:
                definition = next_td.get_text(strip=True)
                if definition:
                    vietnamese_definitions.append(definition)

    # Return list of Vietnamese definitions (UI layer will handle joining)
    vietnamese = vietnamese_definitions

    # Extract audio URL from soundManager.play() call
    audio_url = ""
    audio_span = soup.find("span", onclick=lambda x: bool(x) and "soundManager.play" in x)
    if audio_span:
        onclick = audio_span.get("onclick", "")
        start_idx = onclick.find("'") + 1
        end_idx = onclick.find("'", start_idx)
        audio_url = onclick[start_idx:end_idx]

    # Extract sample sentences
    sentences = parse_sample_sentences(html_content)

    return {
        "pinyin": pinyin,
        "vietnamese": vietnamese,
        "audio_url": audio_url,
        "sentences": sentences,
    }


def parse_sample_sentences(html_content: str) -> list[SampleSentence]:
    """Parse sample sentences from dictionary HTML content.

    Args:
        html_content: The HTML content to parse

    Returns:
        List of dictionaries with 'chinese' and 'vietnamese' keys.
        Returns empty list if no sample sentences found.

    Examples:
        >>> html = '''<TR><TD><IMG src=img/dict/72B02D27.png></TD>
        ...           <TD><FONT color=#FF0000>我爱你。</FONT></TD></TR>
        ...           <TR><TD></TD><TD><FONT COLOR=#7F7F7F>Tôi yêu bạn.</FONT></TD></TR>'''
        >>> result = parse_sample_sentences(html)
        >>> result[0]['chinese']
        '我爱你。'
    """
    soup = BeautifulSoup(html_content, "html.parser")
    sentences = []

    # Find all images that mark sample sentences
    sentence_markers = soup.find_all("img", src=lambda x: bool(x) and "img/dict/72B02D27.png" in x)

    for marker in sentence_markers:
        # Find the parent TD of the marker
        marker_td = marker.find_parent("td")
        if not marker_td:
            continue

        # Get the next sibling TD which contains the Chinese sentence
        chinese_td = marker_td.find_next_sibling("td")
        if not chinese_td:
            continue

        # Extract Chinese sentence from <FONT color=#FF0000> tag
        chinese_font = chinese_td.find("font", color=lambda x: bool(x) and x.lower() == "#ff0000")
        if not chinese_font:
            continue

        chinese_sentence = chinese_font.get_text(strip=True)

        # Find the next row (TR) which contains the Vietnamese translation
        current_tr = marker.find_parent("tr")
        if not current_tr:
            continue

        next_tr = current_tr.find_next_sibling("tr")
        vietnamese_sentence = ""

        if next_tr:
            # Find <FONT COLOR=#7F7F7F> tag with Vietnamese translation
            vietnamese_font = next_tr.find(
                "font", color=lambda x: bool(x) and x.lower() == "#7f7f7f"
            )
            if vietnamese_font:
                vietnamese_sentence = vietnamese_font.get_text(strip=True)

        sentences.append({"chinese": chinese_sentence, "vietnamese": vietnamese_sentence})

    return sentences
