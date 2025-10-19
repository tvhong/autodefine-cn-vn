"""Functions for fetching web content from Chinese-Vietnamese dictionary."""

import urllib.parse
import urllib.request


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

    Note:
        Uses errors='replace' to handle malformed UTF-8 sequences in HTML meta tags.
        Invalid bytes are replaced with the Unicode replacement character (�).
    """
    with urllib.request.urlopen(url, timeout=timeout) as response:
        content_bytes = response.read()
        return content_bytes.decode("utf-8", errors="replace")


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
