import json
from datetime import datetime

from lab.lab_config import PROMOTED_FILE, REJECTED_FILE


def _now():
    return datetime.utcnow().isoformat()


def _load_json(path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _append(path, candidate):
    data = _load_json(path)
    candidate = dict(candidate)
    candidate["saved_at"] = _now()
    data.append(candidate)
    _save_json(path, data)


def add_promoted(candidate):
    _append(PROMOTED_FILE, candidate)


def add_rejected(candidate):
    _append(REJECTED_FILE, candidate)


def load_promoted():
    return _load_json(PROMOTED_FILE)


def load_rejected():
    return _load_json(REJECTED_FILE)
