import json
import hashlib
import re
import os
from pathlib import Path
from datetime import datetime, timezone


# =========================================================
# TEXT
# =========================================================

def clean(x):
    return str(x or "").strip()


def normalize_spaces(text):
    return re.sub(r"\s+", " ", clean(text)).strip()


def short(text, n=300):
    text = normalize_spaces(text)
    if len(text) <= n:
        return text
    return text[:n].rstrip() + "..."


def word_count(text):
    return len(clean(text).split())


def char_count(text):
    return len(clean(text))


def normalize_key(text):
    text = clean(text).lower()
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
    text = text.replace("à", "a").replace("ù", "u").replace("ç", "c")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def contains_any(text, markers):
    text = clean(text).lower()
    return any(clean(m).lower() in text for m in markers)


# =========================================================
# TIME / HASH
# =========================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha_text(text):
    return hashlib.sha256(clean(text).encode("utf-8")).hexdigest()


# =========================================================
# JSON FILES
# =========================================================

def load_json_file(path, default):
    path = Path(path)

    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_file(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    tmp_path.replace(path)


def append_jsonl(path, item):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


# =========================================================
# JSON EXTRACTION
# =========================================================

def extract_json(text):
    text = clean(text)

    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        pass

    # Extract largest JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        chunk = text[start:end + 1]
        try:
            return json.loads(chunk)
        except Exception:
            pass

    # Extract JSON array if needed
    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end > start:
        chunk = text[start:end + 1]
        try:
            return json.loads(chunk)
        except Exception:
            pass

    return None


# =========================================================
# SAFE TYPES
# =========================================================

def safe_list(x):
    if isinstance(x, list):
        return x
    if x is None:
        return []
    return [x]


def safe_dict(x):
    return x if isinstance(x, dict) else {}


def clamp(n, low, high):
    try:
        n = float(n)
    except Exception:
        return low

    return max(low, min(high, n))


def to_int(n, default=0, low=None, high=None):
    try:
        n = int(round(float(n)))
    except Exception:
        return default

    if low is not None:
        n = max(low, n)
    if high is not None:
        n = min(high, n)

    return n


def average(values):
    values = [v for v in values if isinstance(v, (int, float))]
    if not values:
        return 0
    return round(sum(values) / len(values), 2)


# =========================================================
# ENV
# =========================================================

def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return clean(value).lower() in {"1", "true", "yes", "y", "on"}


def env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default