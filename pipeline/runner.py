import time

from config import REQUEST_SLEEP_SECONDS, LOOP_INTERVAL_SECONDS
from utils import console
from utils.run_stats import RunStats
from youtube_client import is_quota_error
from pipeline.collector import collect_target_video_ids
from pipeline.processor import process_video_with_key_fallback, sleep_until_quota_reset


def run_once(client_pool) -> RunStats:
    stats = RunStats()
    youtube = client_pool.get_client()
    video_ids = collect_target_video_ids(youtube, stats)

    console.section("Processando vídeos")

    with console.make_progress() as progress:
        task = progress.add_task(
            "Coletando vídeos",
            total=len(video_ids),
            ok=0,
            skipped=0,
            failed=0,
            comments=0,
        )

        for video_id in video_ids:
            result = process_video_with_key_fallback(client_pool, video_id)

            if result["skipped"]:
                stats.skipped_videos += 1
            elif result["success"]:
                stats.processed_videos += 1
            else:
                stats.failed_videos += 1

            stats.collected_comments += result["comments_count"]

            progress.update(
                task,
                advance=1,
                ok=stats.processed_videos,
                skipped=stats.skipped_videos,
                failed=stats.failed_videos,
                comments=stats.collected_comments,
            )

            if REQUEST_SLEEP_SECONDS > 0:
                time.sleep(REQUEST_SLEEP_SECONDS)

    console.summary(stats)
    return stats


def run_scraper_pipeline(client_pool):
    console.header("YOUTUBE SCRAPER", "Modo: contínuo/incremental")

    while True:
        try:
            run_once(client_pool)

            console.warn(
                f"Ciclo finalizado. Aguardando {LOOP_INTERVAL_SECONDS} segundos "
                f"para próxima execução."
            )
            time.sleep(LOOP_INTERVAL_SECONDS)
            client_pool.reset_keys()

        except KeyboardInterrupt:
            console.warn("Execução interrompida manualmente.")
            break

        except Exception as e:
            if is_quota_error(e):
                rotated = client_pool.rotate_key()

                if rotated:
                    console.warn("Limite da API atingido. Alternando para outra key.")
                    continue

                sleep_until_quota_reset(client_pool)
                continue

            console.fail(f"Erro crítico no pipeline: {e}")
            time.sleep(REQUEST_SLEEP_SECONDS)
