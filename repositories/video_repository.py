from datetime import datetime, timezone

from repositories.paths import video_dir
from storage import save_json


def save_video(video: dict):
    data = {**video, "collected_at": datetime.now(timezone.utc).isoformat()}
    path = video_dir(data["channel_id"], data["video_id"])
    path.mkdir(parents=True, exist_ok=True)
    save_json(path / "video.json", data)
