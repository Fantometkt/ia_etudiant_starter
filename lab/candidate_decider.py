from lab.candidate_registry import add_promoted, add_rejected
from lab.lab_config import (
    LAB_EVAL_VERSION,
    PROMOTION_MARGIN,
    MIN_SCORE_TOLERANCE,
    MIN_ADVERSARIAL_AVG,
    MIN_CORE_AVG,
    MIN_SCORE_FLOOR,
)


def _get_block_average(benchmark, block_name):
    diagnostics = benchmark.get("diagnostics", {})
    by_block = diagnostics.get("by_block", {})
    return by_block.get(block_name, {}).get("average", 0)


def _compute_decision_score(benchmark):
    diagnostics = benchmark.get("diagnostics", {})
    overall = diagnostics.get("overall_average", 0)
    adversarial = _get_block_average(benchmark, "adversarial")
    core = _get_block_average(benchmark, "core")
    return round((overall * 0.5) + (adversarial * 0.3) + (core * 0.2), 2)


def decide_candidate(candidate, baseline_eval, candidate_eval):
    baseline_benchmark = baseline_eval["benchmark"]
    candidate_benchmark = candidate_eval["benchmark"]

    baseline_diag = baseline_benchmark["diagnostics"]
    candidate_diag = candidate_benchmark["diagnostics"]

    baseline_avg = baseline_diag["overall_average"]
    candidate_avg = candidate_diag["overall_average"]

    baseline_min = baseline_diag["min_score"]
    candidate_min = candidate_diag["min_score"]

    adversarial_avg = _get_block_average(candidate_benchmark, "adversarial")
    core_avg = _get_block_average(candidate_benchmark, "core")

    baseline_decision_score = _compute_decision_score(baseline_benchmark)
    candidate_decision_score = _compute_decision_score(candidate_benchmark)

    target_avg = baseline_avg + PROMOTION_MARGIN
    target_min = baseline_min - MIN_SCORE_TOLERANCE

    avg_ok = candidate_avg >= target_avg
    min_ok = candidate_min >= target_min
    floor_ok = candidate_min >= MIN_SCORE_FLOOR
    adversarial_ok = adversarial_avg >= MIN_ADVERSARIAL_AVG
    core_ok = core_avg >= MIN_CORE_AVG
    decision_score_ok = candidate_decision_score >= baseline_decision_score

    decision = "reject"
    failed = []

    if not avg_ok:
        failed.append(f"moyenne insuffisante ({candidate_avg:.2f} < {target_avg:.2f})")

    if not min_ok:
        failed.append(f"min_score trop bas ({candidate_min:.2f} < {target_min:.2f})")

    if not floor_ok:
        failed.append(f"min_score sous le plancher ({candidate_min:.2f} < {MIN_SCORE_FLOOR:.2f})")

    if not adversarial_ok:
        failed.append(
            f"adversarial trop faible ({adversarial_avg:.2f} < {MIN_ADVERSARIAL_AVG:.2f})"
        )

    if not core_ok:
        failed.append(
            f"core trop faible ({core_avg:.2f} < {MIN_CORE_AVG:.2f})"
        )

    if not decision_score_ok:
        failed.append(
            f"decision_score insuffisant ({candidate_decision_score:.2f} < {baseline_decision_score:.2f})"
        )

    if failed:
        reason = "Candidat insuffisant | " + " ; ".join(failed)
    else:
        decision = "promote"
        reason = "Candidat meilleur que la baseline sur le benchmark labo"

    candidate["eval_version"] = LAB_EVAL_VERSION
    candidate["decision_reason"] = reason
    candidate["baseline_average"] = baseline_avg
    candidate["candidate_average"] = candidate_avg
    candidate["baseline_min"] = baseline_min
    candidate["candidate_min"] = candidate_min
    candidate["adversarial_average"] = adversarial_avg
    candidate["core_average"] = core_avg
    candidate["baseline_decision_score"] = baseline_decision_score
    candidate["candidate_decision_score"] = candidate_decision_score

    if decision == "promote":
        add_promoted(candidate)
    else:
        add_rejected(candidate)

    return {
        "decision": decision,
        "reason": reason,
        "baseline_average": baseline_avg,
        "candidate_average": candidate_avg,
        "baseline_min": baseline_min,
        "candidate_min": candidate_min,
        "adversarial_average": adversarial_avg,
        "core_average": core_avg,
        "baseline_decision_score": baseline_decision_score,
        "candidate_decision_score": candidate_decision_score,
        "eval_version": LAB_EVAL_VERSION,
    }
