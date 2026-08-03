import json
from pathlib import Path


def ensure_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists() or path.stat().st_size == 0:
        path.write_text("[]", encoding="utf-8")


def load_json(path: Path):
    ensure_file(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        path.write_text("[]", encoding="utf-8")
        return []


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_unique(path: Path, new_items, key):
    data = load_json(path)

    existing_ids = {item.get(key) for item in data}

    for item in new_items:
        if item.get(key) not in existing_ids:
            data.append(item)
            existing_ids.add(item.get(key))

    save_json(path, data)