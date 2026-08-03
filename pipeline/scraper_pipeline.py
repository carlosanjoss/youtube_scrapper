# Shim de compatibilidade — use pipeline.runner, pipeline.collector e pipeline.processor diretamente.
from pipeline.collector import collect_target_video_ids
from pipeline.processor import process_video, process_video_with_key_fallback, sleep_until_quota_reset
from pipeline.runner import run_once, run_scraper_pipeline

__all__ = [
    "collect_target_video_ids",
    "process_video",
    "process_video_with_key_fallback",
    "sleep_until_quota_reset",
    "run_once",
    "run_scraper_pipeline",
]
