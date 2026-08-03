# Shim de compatibilidade — use utils.text e utils.url diretamente.
from utils.text import normalize_comment_text
from utils.url import extract_video_id, load_targets

__all__ = ["normalize_comment_text", "extract_video_id", "load_targets"]
