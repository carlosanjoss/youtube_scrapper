from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RunStats:
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    started_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    total_targets: int = 0
    total_videos: int = 0
    processed_videos: int = 0
    skipped_videos: int = 0
    failed_videos: int = 0
    collected_comments: int = 0