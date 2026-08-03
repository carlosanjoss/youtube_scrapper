import time

from utils import console
from services.video_service import get_video_info
from services.comment_service import get_video_comments
from repositories.channel_repository import ensure_channel_stub
from repositories.video_repository import save_video
from repositories.comment_repository import save_comments
from repositories.state_repository import (
    is_video_processed,
    mark_video_processed,
    mark_video_failed,
)
from youtube_client import is_quota_error, seconds_until_youtube_quota_reset


def process_video(youtube, video_id: str) -> dict:
    if is_video_processed(video_id):
        return {"success": True, "skipped": True, "comments_count": 0}

    video_info = get_video_info(youtube, video_id)

    if not video_info:
        mark_video_failed(video_id)
        return {"success": False, "skipped": False, "comments_count": 0}

    channel_id = video_info["channel_id"]

    ensure_channel_stub(channel_id, video_info["channel_title"])
    save_video(video_info)

    comments = get_video_comments(youtube, video_id)
    save_comments(comments, channel_id, video_id)

    mark_video_processed(video_id)

    return {"success": True, "skipped": False, "comments_count": len(comments)}


def sleep_until_quota_reset(client_pool):
    seconds = seconds_until_youtube_quota_reset()
    console.warn(
        f"Todas as API keys atingiram limite. "
        f"Aguardando {seconds} segundos até o reset da quota."
    )
    time.sleep(seconds)
    client_pool.reset_keys()


def process_video_with_key_fallback(client_pool, video_id: str) -> dict:
    while True:
        youtube = client_pool.get_client()

        try:
            return process_video(youtube, video_id)

        except Exception as e:
            if not is_quota_error(e):
                console.fail(f"Erro inesperado no vídeo {video_id}: {e}")
                mark_video_failed(video_id)
                return {"success": False, "skipped": False, "comments_count": 0}

            rotated = client_pool.rotate_key()

            if rotated:
                console.warn("Limite da API atingido. Alternando para outra key.")
                continue

            sleep_until_quota_reset(client_pool)
