import json
import hashlib
from datetime import datetime

def clean(x):
    return (x or "").strip()

def now_iso():
    return datetime.utcnow().isoformat()

def sha_text(text):
    return hashlib.sha256(clean(text).encode("utf-8")).hexdigest()

def load_json_file(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        chunk = text[start:end + 1]
        try:
            return json.loads(chunk)
        except Exception:
            return None
    return None