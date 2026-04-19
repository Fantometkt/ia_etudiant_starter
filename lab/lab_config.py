from pathlib import Path

LAB_EVAL_VERSION = "v2_strict_judge"

LAB_DIR = Path(__file__).resolve().parent
DATA_DIR = LAB_DIR / "data" / LAB_EVAL_VERSION

PROMOTED_FILE = DATA_DIR / "promoted.json"
REJECTED_FILE = DATA_DIR / "rejected.json"
BEST_FILE = DATA_DIR / "best_candidate.json"

PROMOTION_MARGIN = 0.75
MIN_SCORE_TOLERANCE = 2
MIN_ADVERSARIAL_AVG = 33.0
MIN_CORE_AVG = 33.0
MIN_SCORE_FLOOR = 28.0

DATA_DIR.mkdir(parents=True, exist_ok=True)
