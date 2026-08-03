from datetime import datetime, timezone

from repositories.paths import channel_dir
from storage import save_json


def save_channel(channel_info: dict):
    data = {**channel_info, "collected_at": datetime.now(timezone.utc).isoformat()}
    path = channel_dir(data["channel_id"]) / "channel.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_json(path, data)


def ensure_channel_stub(channel_id: str, channel_title: str):
    path = channel_dir(channel_id) / "channel.json"
    if not path.exists():
        save_channel({"channel_id": channel_id, "channel_title": channel_title})
