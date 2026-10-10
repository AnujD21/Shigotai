"""Text helpers shared by job-source adapters."""

import html
import re
from html.parser import HTMLParser

_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article"}
_CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿ｦ-ﾟ]")
_LATIN = re.compile(r"[A-Za-z]")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag in _BLOCK_TAGS and tag != "li":  # the next <li> already starts a new line
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def html_to_text(markup: str | None) -> str:
    """Readable plain text from posting HTML, keeping paragraph and list
    structure (the requirement extractor relies on "Required:" / "Preferred:"
    sections staying on separate lines)."""
    if not markup:
        return ""
    # Greenhouse double-encodes its HTML ("&lt;p&gt;"), so unescape first.
    if "&lt;" in markup and "<" not in markup:
        markup = html.unescape(markup)
    parser = _TextExtractor()
    parser.feed(markup)
    parser.close()
    text = "".join(parser.parts).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def detect_language(text: str) -> str:
    """'ja', 'en', or 'mixed' from the share of Japanese characters."""
    cjk = len(_CJK.findall(text))
    latin = len(_LATIN.findall(text))
    total = cjk + latin
    if total == 0:
        return "en"
    # A Japanese character carries roughly a word's worth of meaning, while
    # Latin is counted per letter, so weight CJK up before comparing.
    share = (cjk * 4) / (cjk * 4 + latin)
    if share > 0.7:
        return "ja"
    if share > 0.15:
        return "mixed"
    return "en"
