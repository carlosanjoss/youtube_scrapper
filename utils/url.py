import re
from pathlib import Path
from urllib.parse import unquote


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)",
        r"shorts/([^?&]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def parse_channel_target(value: str) -> tuple[str, str] | None:
    """Return the channels.list lookup field and value for an ID or @handle."""
    target = unquote(value.strip())
    if re.fullmatch(r"UC[\w-]+", target):
        return "id", target

    channel_match = re.search(r"youtube\.com/channel/(UC[\w-]+)", target, re.I)
    if channel_match:
        return "id", channel_match.group(1)

    handle_match = re.search(r"(?:youtube\.com/)?@([^/?#]+)", target, re.I)
    if handle_match:
        return "forHandle", handle_match.group(1)

    user_match = re.search(r"youtube\.com/user/([^/?#]+)", target, re.I)
    if user_match:
        return "forUsername", user_match.group(1)

    custom_match = re.search(r"youtube\.com/(?:c/)?([^/?#]+)", target, re.I)
    if custom_match and custom_match.group(1).lower() not in {
        "watch",
        "shorts",
        "playlist",
        "live",
    }:
        return "forHandle", custom_match.group(1)

    return None


def load_targets(path: Path) -> list[str]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
