from utils import console
from utils.text import normalize_comment_text
from youtube_client import execute_with_key_fallback, is_quota_error


def _execute(youtube, request_factory, client_pool=None):
    if client_pool is not None:
        return execute_with_key_fallback(client_pool, request_factory)
    return request_factory(youtube).execute()


def build_comment_payload(comment: dict, video_id: str, parent_id=None, is_reply=False):
    snippet = comment["snippet"]
    raw_text = snippet.get("textDisplay")

    return {
        "comment_id": comment.get("id"),
        "video_id": video_id,
        "parent_id": parent_id,
        "is_reply": is_reply,
        "author": snippet.get("authorDisplayName"),
        "text": normalize_comment_text(raw_text),
        "text_raw": raw_text,
        "like_count": snippet.get("likeCount"),
        "published_at": snippet.get("publishedAt"),
        "updated_at": snippet.get("updatedAt")
    }


def _fetch_all_replies(youtube, thread_id: str, video_id: str, client_pool=None):
    """Busca todas as respostas de um thread via paginação."""
    replies = []
    next_page_token = None

    while True:
        try:
            response = _execute(
                youtube,
                lambda client: client.comments().list(
                    part="snippet",
                    parentId=thread_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=next_page_token,
                ),
                client_pool,
            )

        except Exception as e:
            if is_quota_error(e):
                raise

            console.fail(f"Erro ao buscar respostas do thread {thread_id}: {e}")
            break

        for comment in response.get("items", []):
            replies.append(
                build_comment_payload(comment, video_id, parent_id=thread_id, is_reply=True)
            )

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return replies


def get_video_comments(youtube, video_id: str, client_pool=None):
    comments = []
    next_page_token = None

    while True:
        try:
            response = _execute(
                youtube,
                lambda client: client.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=next_page_token,
                ),
                client_pool,
            )

        except Exception as e:
            if is_quota_error(e):
                raise

            error_text = str(e)

            if "commentsDisabled" in error_text:
                console.warn(f"Comentários desativados: {video_id}")
            elif "videoNotFound" in error_text:
                console.warn(f"Vídeo não encontrado ao coletar comentários: {video_id}")
            else:
                console.fail(f"Erro ao coletar comentários do vídeo {video_id}: {e}")

            break

        for item in response.get("items", []):
            thread_id = item.get("id")
            top_comment = item["snippet"]["topLevelComment"]
            total_replies = item["snippet"].get("totalReplyCount", 0)
            bundled_replies = item.get("replies", {}).get("comments", [])

            comments.append(
                build_comment_payload(top_comment, video_id, parent_id=None, is_reply=False)
            )

            if total_replies > len(bundled_replies):
                # A API retorna no máximo 5 respostas bundled; busca todas via paginação
                comments.extend(
                    _fetch_all_replies(
                        youtube,
                        thread_id,
                        video_id,
                        client_pool=client_pool,
                    )
                )
            else:
                for reply in bundled_replies:
                    comments.append(
                        build_comment_payload(reply, video_id, parent_id=thread_id, is_reply=True)
                    )

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return comments
