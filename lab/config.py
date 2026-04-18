LAB_NAME = "ia_etudiant_lab"

MAX_ACTIVE_CANDIDATES = 50
MAX_PROMOTED_HISTORY = 50
MAX_REJECTED_HISTORY = 200
MAX_REPORTS_HISTORY = 200

QUICK_ACCEPT_THRESHOLD = 38
QUICK_REVIEW_THRESHOLD = 34
FULL_ACCEPT_THRESHOLD = 40
ULTRA_ACCEPT_THRESHOLD = 42

AUTO_PROMOTION_ENABLED = False
HUMAN_VALIDATION_REQUIRED = True

DEFAULT_MUTATION_INTENSITY = "low"

STATE_FILES = {
    "candidates": "lab/state/candidates.json",
    "promoted": "lab/state/promoted.json",
    "rejected": "lab/state/rejected.json",
    "lab_stats": "lab/state/lab_stats.json",
}