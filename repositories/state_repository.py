from datetime import datetime, timezone

from config import STATE_OUTPUT
from storage import load_json, save_json


_DEFAULT: dict = {
    "processed_videos": [],
    "failed_videos": [],
    "last_run_at": None,
}

_cache: dict | None = None


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache

    try:
        state = load_json(STATE_OUTPUT)

        if isinstance(state, list):
            state = _DEFAULT.copy()
        else:
            for key, value in _DEFAULT.items():
                state.setdefault(key, value)

    except Exception:
        state = _DEFAULT.copy()

    _cache = state
    return _cache


def _persist(state: dict):
    state["last_run_at"] = datetime.now(timezone.utc).isoformat()
    save_json(STATE_OUTPUT, state)


def is_video_processed(video_id: str) -> bool:
    return video_id in _load()["processed_videos"]


def mark_video_processed(video_id: str):
    state = _load()
    if video_id not in state["processed_videos"]:
        state["processed_videos"].append(video_id)
    _persist(state)


def mark_video_failed(video_id: str):
    state = _load()
    if video_id not in state["failed_videos"]:
        state["failed_videos"].append(video_id)
    _persist(state)
