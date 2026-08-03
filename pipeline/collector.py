from config import VIDEOS_FILE, CHANNELS_FILE
from utils import console
from utils.url import extract_video_id, load_targets
from utils.run_stats import RunStats
from services.channel_service import get_channel_info, get_channel_video_ids
from repositories.channel_repository import save_channel


def collect_target_video_ids(youtube, stats: RunStats) -> list[str]:
    video_urls = load_targets(VIDEOS_FILE)
    channel_ids = load_targets(CHANNELS_FILE)

    console.section("Carregando alvos")
    console.info("Links de vídeos", len(video_urls))
    console.info("Canais", len(channel_ids))

    stats.total_targets = len(video_urls) + len(channel_ids)

    video_ids: list[str] = []

    for url in video_urls:
        video_id = extract_video_id(url)
        if video_id:
            video_ids.append(video_id)
        else:
            console.warn(f"Não foi possível extrair video_id: {url}")

    for channel_id in channel_ids:
        channel_info = get_channel_info(youtube, channel_id)

        if not channel_info:
            console.warn(f"Canal ignorado: {channel_id}")
            continue

        save_channel(channel_info)

        channel_video_ids = get_channel_video_ids(
            youtube, channel_id, channel_info["uploads_playlist_id"]
        )
        video_ids.extend(channel_video_ids)
        console.ok(f"Canal {channel_info['channel_title']}: {len(channel_video_ids)} vídeos")

    video_ids = list(dict.fromkeys(video_ids))
    stats.total_videos = len(video_ids)
    console.ok(f"{len(video_ids)} vídeos únicos encontrados")

    return video_ids
