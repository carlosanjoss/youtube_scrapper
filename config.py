from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_KEYS = [
    key.strip()
    for key in os.getenv("YOUTUBE_API_KEYS", "").split(",")
    if key.strip()
]

if not YOUTUBE_API_KEYS and YOUTUBE_API_KEY:
    YOUTUBE_API_KEYS = [YOUTUBE_API_KEY]

REQUEST_SLEEP_SECONDS = int(os.getenv("REQUEST_SLEEP_SECONDS", "1"))
LOOP_INTERVAL_SECONDS = int(os.getenv("LOOP_INTERVAL_SECONDS", "1800"))

BASE_DIR = Path(__file__).resolve().parent
TARGETS_DIR = BASE_DIR / "targets"
DATA_DIR = BASE_DIR / "data"

VIDEOS_FILE = TARGETS_DIR / "videos.txt"
CHANNELS_FILE = TARGETS_DIR / "channels.txt"

CHANNELS_DIR = DATA_DIR / "channels"

# legacy flat files (usados pelo script de migração)
VIDEOS_OUTPUT = DATA_DIR / "videos.json"
COMMENTS_OUTPUT = DATA_DIR / "comments.json"

STATE_OUTPUT = DATA_DIR / "state.json"

