"""Functions for fetching and parsing Chinese-Vietnamese dictionary content."""

import urllib.error
import urllib.request

from bs4 import BeautifulSoup


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


def parse_dictionary_content(html_content: str) -> dict[str, str]:
    """Parse pinyin and Vietnamese definition from dictionary HTML content.

    Args:
        html_content: The HTML content to parse

    Returns:
        Dictionary with 'pinyin' and 'vietnamese' keys.
        Returns empty strings for missing data.

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

    # Extract Vietnamese definition from the table containing TD elements with class="tacon"
    vietnamese = ""
    # Find all tables and look for the one with class="tacon" cells
    for table in soup.find_all("table"):
        # Only get direct child TR elements to avoid nested tables
        rows = table.find_all("tr", recursive=False)
        if len(rows) >= 2:
            # Look for the first row with 3 TDs (definition row)
            # Rows with 2 TDs typically contain metadata like pinyin, radicals, etc.
            for row in rows[1:]:  # Skip first row (usually contains pinyin)
                tds = row.find_all("td", class_="tacon", recursive=False)
                if len(tds) >= 3:
                    # Get the last TD which contains the Vietnamese definition
                    vietnamese = tds[-1].get_text(strip=True)
                    break
            if vietnamese:
                break

    return {"pinyin": pinyin, "vietnamese": vietnamese}
