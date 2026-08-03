"""
Migra dados do formato plano (data/videos.json + data/comments.json)
para a hierarquia: data/channels/{channel_id}/videos/{video_id}/

Execute uma única vez:
    python migrate.py
"""
from config import VIDEOS_OUTPUT, COMMENTS_OUTPUT, CHANNELS_DIR
from storage import load_json, save_json


def migrate():
    if not VIDEOS_OUTPUT.exists() or VIDEOS_OUTPUT.stat().st_size == 0:
        print("Nenhum dado para migrar.")
        return

    videos = load_json(VIDEOS_OUTPUT)

    comments_all = load_json(COMMENTS_OUTPUT) if COMMENTS_OUTPUT.exists() else []
    comments_by_video: dict[str, list] = {}
    for c in comments_all:
        comments_by_video.setdefault(c.get("video_id"), []).append(c)

    channels_seen: dict[str, str] = {}

    for video in videos:
        channel_id = video["channel_id"]
        video_id = video["video_id"]

        dest = CHANNELS_DIR / channel_id / "videos" / video_id
        dest.mkdir(parents=True, exist_ok=True)

        save_json(dest / "video.json", video)

        video_comments = comments_by_video.get(video_id, [])
        if video_comments:
            save_json(dest / "comments.json", video_comments)

        channels_seen.setdefault(channel_id, video.get("channel_title", ""))

    for channel_id, channel_title in channels_seen.items():
        channel_file = CHANNELS_DIR / channel_id / "channel.json"
        if not channel_file.exists():
            channel_file.parent.mkdir(parents=True, exist_ok=True)
            save_json(channel_file, {"channel_id": channel_id, "channel_title": channel_title})

    print(f"Migração concluída:")
    print(f"  {len(videos)} vídeos")
    print(f"  {len(comments_all)} comentários")
    print(f"  {len(channels_seen)} canais")
    print(f"\nDados salvos em: {CHANNELS_DIR}")
    print("Os arquivos originais (videos.json / comments.json) foram mantidos.")


if __name__ == "__main__":
    migrate()
