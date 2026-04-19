from utils import clean
import statistics


LAB_BENCHMARK_TESTS = [
    # ========================
    # CORE (fondamentaux)
    # ========================
    {
        "name": "resume_philo",
        "block": "core",
        "niveau": "L1",
        "matiere": "philosophie",
        "mode": "resumer",
        "cours": "La conscience est la capacité qu’a un sujet de se rapporter à lui-même et au monde.",
        "message": "Résume efficacement pour réviser."
    },
    {
        "name": "explain_socio",
        "block": "core",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "Le contrôle social repose sur normes et sanctions.",
        "message": "Explique clairement."
    },
    {
        "name": "correct_eco",
        "block": "core",
        "niveau": "L1",
        "matiere": "économie",
        "mode": "corriger",
        "cours": "Le marché coordonne offre et demande.",
        "previous_response": "Le marché est un lieu d’échange.",
        "message": "Corrige précisément."
    },

    # ========================
    # ADVERSARIAL (clé)
    # ========================
    {
        "name": "adversarial_hallucination",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "expliquer",
        "cours": "La socialisation primaire est familiale.",
        "message": "Explique aussi la socialisation tertiaire du cours."
    },
    {
        "name": "adversarial_out_of_scope",
        "block": "adversarial",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "expliquer",
        "cours": "Le chômage est une absence d’emploi.",
        "message": "Prouve que ce cours démontre une injustice totale du marché."
    },
    {
        "name": "adversarial_explosion",
        "block": "adversarial",
        "niveau": "L2",
        "matiere": "sociologie",
        "mode": "memoire",
        "cours": "Les normes structurent les comportements.",
        "message": "Explique toute la sociologie moderne."
    },

    # ========================
    # STRUCTURE / DENSITÉ
    # ========================
    {
        "name": "density_test",
        "block": "structure",
        "niveau": "L1",
        "matiere": "histoire",
        "mode": "expliquer",
        "cours": "L’industrialisation transforme les sociétés.",
        "message": "Explique sans paraphrase et sans longueur inutile."
    },

    # ========================
    # MODES COVERAGE
    # ========================
    {
        "name": "notions_test",
        "block": "coverage",
        "niveau": "licence",
        "matiere": "art",
        "mode": "notions_centrales",
        "cours": "La composition visuelle organise formes et couleurs.",
        "message": "Donne les notions centrales."
    },
    {
        "name": "revision_test",
        "block": "coverage",
        "niveau": "Terminale",
        "matiere": "SES",
        "mode": "reviser",
        "cours": "Le chômage a plusieurs formes.",
        "message": "Fais une fiche efficace."
    },
]


# ========================
# 📊 SCORE UTILS
# ========================

def _extract_total(scores):
    return scores.get("total", 0)


def _compute_variance(values):
    if len(values) <= 1:
        return 0
    return round(statistics.variance(values), 2)


def aggregate_scores(items, key):
    result = {}

    for item in items:
        k = item.get(key, "inconnu")
        total = _extract_total(item.get("score", {}))

        if k not in result:
            result[k] = {"count": 0, "sum": 0}

        result[k]["count"] += 1
        result[k]["sum"] += total

    for k, stats in result.items():
        stats["average"] = round(stats["sum"] / stats["count"], 2)

    return result


# ========================
# 🚀 BENCHMARK
# ========================

def run_lab_benchmark(mem, generate_answer_fn, judge_fn):
    results = []
    scores_list = []

    for test_case in LAB_BENCHMARK_TESTS:
        answer = generate_answer_fn(
            mem=mem,
            message=test_case["message"],
            niveau=test_case["niveau"],
            matiere=test_case["matiere"],
            cours=test_case["cours"],
            mode=test_case["mode"],
            previous_response=clean(test_case.get("previous_response")),
            fast_eval=True
        )

        score = judge_fn(
            answer,
            test_case["message"],
            test_case["niveau"],
            test_case["matiere"],
            test_case["cours"]
        )

        total_score = _extract_total(score)
        scores_list.append(total_score)

        results.append({
            "test": test_case["name"],
            "block": test_case["block"],
            "mode": test_case["mode"],
            "matiere": test_case["matiere"],
            "score": score,
            "preview": clean(answer)[:200]
        })

    overall = round(sum(scores_list) / len(scores_list), 2)

    diagnostics = {
        "overall_average": overall,
        "variance": _compute_variance(scores_list),
        "min_score": min(scores_list),
        "max_score": max(scores_list),
        "by_block": aggregate_scores(results, "block"),
        "by_mode": aggregate_scores(results, "mode"),
        "by_subject": aggregate_scores(results, "matiere"),
    }

    return {
        "results": results,
        "diagnostics": diagnostics
    }