import json

from lab.candidate_registry import load_promoted
from lab.lab_config import BEST_FILE


def _score_candidate(candidate):
    return candidate.get("candidate_decision_score", candidate.get("candidate_average", 0))


def select_best():
    promoted = load_promoted()

    if not promoted:
        print("Aucun candidat promu trouvé.")
        return None

    best = max(promoted, key=_score_candidate)
    print(f"Meilleur score : {_score_candidate(best)}")
    return best


def save_best(best):
    if not best:
        return

    BEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BEST_FILE, "w", encoding="utf-8") as f:
        json.dump(best, f, indent=2, ensure_ascii=False)

    print(f"Meilleur candidat sauvegardé : {BEST_FILE}")
