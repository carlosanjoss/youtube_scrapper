from utils import console
from utils.text import to_int
from utils.url import parse_channel_target
from youtube_client import execute_with_key_fallback, is_quota_error


def _execute(youtube, request_factory, client_pool=None):
    if client_pool is not None:
        return execute_with_key_fallback(client_pool, request_factory)
    return request_factory(youtube).execute()


def get_channel_info(youtube, channel_target: str, client_pool=None) -> dict | None:
    lookup = parse_channel_target(channel_target)
    if not lookup:
        console.warn(f"Alvo de canal inválido: {channel_target}")
        return None

    lookup_field, lookup_value = lookup
    try:
        params = {"part": "snippet,statistics,contentDetails", lookup_field: lookup_value}
        response = _execute(
            youtube,
            lambda client: client.channels().list(**params),
            client_pool,
        )

        items = response.get("items", [])

        if not items:
            console.warn(f"Canal não encontrado: {channel_target}")
            return None

        item = items[0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        return {
            "channel_id": item.get("id", lookup_value),
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

        console.fail(f"Erro ao buscar canal {channel_target}: {e}")
        return None


def get_channel_video_ids(
    youtube,
    channel_id: str,
    uploads_playlist_id: str,
    client_pool=None,
) -> list[str]:
    video_ids = []
    next_page_token = None

    while True:
        try:
            response = _execute(
                youtube,
                lambda client: client.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token,
                ),
                client_pool,
            )

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
