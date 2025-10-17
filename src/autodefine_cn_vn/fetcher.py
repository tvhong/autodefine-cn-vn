"""Functions for fetching and parsing Chinese-Vietnamese dictionary content."""

import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


def format_url(url_template: str, chinese_word: str) -> str:
    """Format URL by replacing placeholder with URL-encoded Chinese word.

    Args:
        url_template: URL template string with {} placeholder
        chinese_word: Chinese word to insert into URL

    Returns:
        Formatted URL with URL-encoded Chinese word inserted

    Examples:
        >>> format_url("http://example.com?word={}", "你好")
        'http://example.com?word=%E4%BD%A0%E5%A5%BD'
    """
    encoded_word = urllib.parse.quote(chinese_word)
    return url_template.format(encoded_word)


def fetch_webpage(url: str, timeout: int) -> str:
    """Fetch webpage content from the given URL.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        The webpage content as a UTF-8 decoded string

    Raises:
        urllib.error.URLError: If there's a network error or timeout
        urllib.error.HTTPError: If the server returns an HTTP error (404, 500, etc.)
    """
    with urllib.request.urlopen(url, timeout=timeout) as response:
        content_bytes = response.read()
        return content_bytes.decode("utf-8")


def parse_dictionary_content(html_content: str) -> dict[str, str | list[dict[str, str]]]:
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

    # Extract Vietnamese definition by finding the TD after the one with the marker image
    vietnamese = ""
    # Find the img tag with the specific marker image
    marker_img = soup.find("img", src=lambda x: bool(x) and "img/dict/CB1FF077.png" in x)
    if marker_img:
        # Find the parent TD of the marker image
        marker_td = marker_img.find_parent("td")
        if marker_td:
            # Get the next sibling TD which contains the Vietnamese definition
            next_td = marker_td.find_next_sibling("td")
            if next_td:
                vietnamese = next_td.get_text(strip=True)

    # Extract audio URL from soundManager.play() call
    audio_url = ""
    audio_span = soup.find("span", onclick=lambda x: bool(x) and "soundManager.play" in x)
    if audio_span:
        onclick = audio_span.get("onclick", "")
        start_idx = onclick.find("'") + 1
        end_idx = onclick.find("'", start_idx)
        audio_url = onclick[start_idx:end_idx]

    # Extract Chinese word from <span class="thisword"> tag
    chinese_word = ""
    thisword_span = soup.find("span", class_="thisword")
    if thisword_span:
        font_tag = thisword_span.find("font")
        if font_tag:
            chinese_word = font_tag.get_text(strip=True)

    # Extract sample sentences
    sentences = []
    if chinese_word:
        sentences = parse_sample_sentences(html_content, chinese_word)

    return {
        "pinyin": pinyin,
        "vietnamese": vietnamese,
        "audio_url": audio_url,
        "sentences": sentences,
    }


def parse_sample_sentences(html_content: str, chinese_word: str) -> list[dict[str, str]]:
    """Parse sample sentences from dictionary HTML content.

    Args:
        html_content: The HTML content to parse
        chinese_word: The Chinese word being looked up (currently unused)

    Returns:
        List of dictionaries with 'chinese' and 'vietnamese' keys.
        Returns empty list if no sample sentences found.

    Examples:
        >>> html = '''<TR><TD><IMG src=img/dict/72B02D27.png></TD>
        ...           <TD><FONT color=#FF0000>我爱你。</FONT></TD></TR>
        ...           <TR><TD></TD><TD><FONT COLOR=#7F7F7F>Tôi yêu bạn.</FONT></TD></TR>'''
        >>> result = parse_sample_sentences(html, "你")
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


def fetch_audio(audio_url: str, base_url: str, timeout: int) -> bytes:
    """Fetch audio file from the given URL.

    Args:
        audio_url: Relative audio URL path (e.g., '/mp3.php?id=...')
        base_url: Base URL of the dictionary site (e.g., 'http://2.vndic.net')
        timeout: Request timeout in seconds

    Returns:
        The audio file content as bytes

    Raises:
        urllib.error.URLError: If there's a network error or timeout
        urllib.error.HTTPError: If the server returns an HTTP error (404, 500, etc.)
    """
    # Construct full URL if audio_url is relative
    full_url = base_url.rstrip("/") + audio_url if audio_url.startswith("/") else audio_url

    with urllib.request.urlopen(full_url, timeout=timeout) as response:
        return response.read()
