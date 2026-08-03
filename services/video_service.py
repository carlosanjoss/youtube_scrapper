from utils import console
from utils.text import to_int
from youtube_client import is_quota_error


def get_video_info(youtube, video_id: str) -> dict | None:
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        items = response.get("items", [])

        if not items:
            console.warn(f"Vídeo não encontrado, privado ou indisponível: {video_id}")
            return None

        item = items[0]
        snippet = item["snippet"]
        statistics = item.get("statistics", {})

        return {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "video_title": snippet.get("title"),
            "video_description": snippet.get("description"),
            "published_at": snippet.get("publishedAt"),
            "view_count": to_int(statistics.get("viewCount")),
            "like_count": to_int(statistics.get("likeCount")),
            "comment_count": to_int(statistics.get("commentCount")),
        }

    except Exception as e:
        if is_quota_error(e):
            raise

        console.fail(f"Erro ao buscar metadados do vídeo {video_id}: {e}")
        return None
