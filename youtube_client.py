from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import YOUTUBE_API_KEYS
from utils import console


def is_quota_error(error):
    text = str(error)

    quota_terms = [
        "quotaExceeded",
        "dailyLimitExceeded",
        "userRateLimitExceeded",
        "rateLimitExceeded"
    ]

    return any(term in text for term in quota_terms)


def seconds_until_youtube_quota_reset():
    pacific = ZoneInfo("America/Los_Angeles")
    now = datetime.now(pacific)

    tomorrow = now.date() + timedelta(days=1)
    reset_time = datetime.combine(
        tomorrow,
        datetime.min.time(),
        tzinfo=pacific
    )

    return max(60, int((reset_time - now).total_seconds()))


class YouTubeClientPool:
    def __init__(self):
        if not YOUTUBE_API_KEYS:
            raise ValueError("Nenhuma API key encontrada em YOUTUBE_API_KEYS")

        self.keys = YOUTUBE_API_KEYS
        self.index = 0
        self.exhausted_indexes = set()

    def get_client(self):
        return build(
            "youtube",
            "v3",
            developerKey=self.keys[self.index]
        )

    def current_key_number(self):
        return self.index + 1

    def rotate_key(self):
        self.exhausted_indexes.add(self.index)

        available_indexes = [
            index
            for index in range(len(self.keys))
            if index not in self.exhausted_indexes
        ]

        if not available_indexes:
            return False

        self.index = available_indexes[0]

        console.warn(
            f"Quota atingida. Alternando para API key "
            f"{self.index + 1}/{len(self.keys)}"
        )

        return True

    def reset_keys(self):
        self.exhausted_indexes.clear()
        self.index = 0