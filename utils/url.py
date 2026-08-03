import re
from pathlib import Path


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


def load_targets(path: Path) -> list[str]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
