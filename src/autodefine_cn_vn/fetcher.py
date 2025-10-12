"""Functions for fetching and parsing Chinese-Vietnamese dictionary content."""

import urllib.error
import urllib.request


def format_url(url_template: str, chinese_word: str) -> str:
    """Format URL by replacing placeholder with Chinese word.

    Args:
        url_template: URL template string with {} placeholder
        chinese_word: Chinese word to insert into URL

    Returns:
        Formatted URL with Chinese word inserted

    Examples:
        >>> format_url("http://example.com?word={}", "你好")
        'http://example.com?word=你好'
    """
    return url_template.format(chinese_word)


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
