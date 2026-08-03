from repositories.paths import video_dir
from storage import save_json


def save_comments(comments: list, channel_id: str, video_id: str):
    if not comments:
        return
    path = video_dir(channel_id, video_id)
    path.mkdir(parents=True, exist_ok=True)
    save_json(path / "comments.json", comments)
