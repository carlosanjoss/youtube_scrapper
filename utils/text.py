import re
import html


def to_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_comment_text(text: str | None) -> str:
    if text is None:
        return ""

    text = html.unescape(text)
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()
