import json
import os
from datetime import datetime


def now_iso():
    return datetime.now().isoformat()


def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_json_item(path, item, default_list=None, max_len=None):
    if default_list is None:
        default_list = []

    data = load_json(path, default_list)

    if not isinstance(data, list):
        data = default_list

    data.append(item)

    if max_len is not None:
        data = data[-max_len:]

    save_json(path, data)
    return data