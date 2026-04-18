from lab.config import STATE_FILES, MAX_ACTIVE_CANDIDATES, MAX_PROMOTED_HISTORY, MAX_REJECTED_HISTORY
from lab.lab_utils import load_json, save_json, now_iso


def load_candidates():
    return load_json(STATE_FILES["candidates"], [])


def save_candidates(candidates):
    save_json(STATE_FILES["candidates"], candidates)


def register_candidate(candidate):
    candidates = load_candidates()
    candidate["created_at"] = now_iso()
    candidates.append(candidate)
    candidates = candidates[-MAX_ACTIVE_CANDIDATES:]
    save_candidates(candidates)
    return candidate


def load_promoted():
    return load_json(STATE_FILES["promoted"], [])


def add_promoted(candidate):
    promoted = load_promoted()
    candidate["promoted_at"] = now_iso()
    promoted.append(candidate)
    promoted = promoted[-MAX_PROMOTED_HISTORY:]
    save_json(STATE_FILES["promoted"], promoted)


def load_rejected():
    return load_json(STATE_FILES["rejected"], [])


def add_rejected(candidate):
    rejected = load_rejected()
    candidate["rejected_at"] = now_iso()
    rejected.append(candidate)
    rejected = rejected[-MAX_REJECTED_HISTORY:]
    save_json(STATE_FILES["rejected"], rejected)