from utils import console
from utils.text import to_int
from youtube_client import is_quota_error


def get_channel_info(youtube, channel_id: str) -> dict | None:
    try:
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        ).execute()

        items = response.get("items", [])

        if not items:
            console.warn(f"Canal não encontrado: {channel_id}")
            return None

        item = items[0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        return {
            "channel_id": channel_id,
            "channel_title": snippet.get("title"),
            "custom_url": snippet.get("customUrl"),
            "description": snippet.get("description"),
            "country": snippet.get("country"),
            "published_at": snippet.get("publishedAt"),
            "subscriber_count": to_int(stats.get("subscriberCount")),
            "video_count": to_int(stats.get("videoCount")),
            "view_count": to_int(stats.get("viewCount")),
            "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
        }

    except Exception as e:
        if is_quota_error(e):
            raise

        console.fail(f"Erro ao buscar canal {channel_id}: {e}")
        return None


def get_channel_video_ids(youtube, channel_id: str, uploads_playlist_id: str) -> list[str]:
    video_ids = []
    next_page_token = None

    while True:
        try:
            response = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

        except Exception as e:
            if is_quota_error(e):
                raise

            console.fail(f"Erro ao listar vídeos do canal {channel_id}: {e}")
            break

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return video_ids
