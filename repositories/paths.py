from pathlib import Path
from config import CHANNELS_DIR


def channel_dir(channel_id: str) -> Path:
    return CHANNELS_DIR / channel_id


def video_dir(channel_id: str, video_id: str) -> Path:
    return channel_dir(channel_id) / "videos" / video_id
