import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from youtube_client import YouTubeClientPool
from pipeline import run_scraper_pipeline


def main():
    client_pool = YouTubeClientPool()
    run_scraper_pipeline(client_pool)


if __name__ == "__main__":
    main()
