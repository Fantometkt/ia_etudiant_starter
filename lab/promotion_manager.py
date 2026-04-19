from lab.candidate_registry import add_promoted, add_rejected


PROMOTION_MARGIN = 0.5
MIN_SCORE_TOLERANCE = 2
MIN_ADVERSARIAL_AVG = 32

STRONG_PROMOTION_MARGIN = 1.25


def decide_candidate(candidate, baseline_eval, candidate_eval):
    baseline_diag = baseline_eval["benchmark"]["diagnostics"]
    candidate_diag = candidate_eval["benchmark"]["diagnostics"]

    baseline_avg = baseline_diag["overall_average"]
    candidate_avg = candidate_diag["overall_average"]

    baseline_min = baseline_diag["min_score"]
    candidate_min = candidate_diag["min_score"]

    candidate_block_scores = candidate_diag["by_block"]
    adversarial_avg = candidate_block_scores.get("adversarial", {}).get("average", 0)

    # ========================
    # 🎯 OBJECTIFS
    # ========================

    target_avg = baseline_avg + PROMOTION_MARGIN
    strong_target_avg = baseline_avg + STRONG_PROMOTION_MARGIN
    target_min = baseline_min - MIN_SCORE_TOLERANCE

    avg_ok = candidate_avg >= target_avg
    min_ok = candidate_min >= target_min
    adversarial_ok = adversarial_avg >= MIN_ADVERSARIAL_AVG

    strong_avg = candidate_avg >= strong_target_avg

    decision = "reject"
    failed = []

    if not avg_ok:
        failed.append(f"moyenne insuffisante ({candidate_avg:.2f} < {target_avg:.2f})")

    if not min_ok:
        failed.append(f"min_score trop bas ({candidate_min:.2f} < {target_min:.2f})")

    if not adversarial_ok:
        failed.append(
            f"adversarial trop faible ({adversarial_avg:.2f} < {MIN_ADVERSARIAL_AVG:.2f})"
        )

    # ========================
    # 🧠 LOGIQUE DE DÉCISION
    # ========================

    if strong_avg and adversarial_ok:
        decision = "promote"
        reason = "Amélioration forte détectée (promotion agressive)"

    elif avg_ok and min_ok and adversarial_ok:
        decision = "promote"
        reason = "Candidat meilleur que la baseline"

    elif avg_ok and adversarial_ok:
        decision = "soft_promote"
        reason = "Amélioration partielle mais intéressante"

    else:
        reason = "Candidat insuffisant"
        if failed:
            reason += " | " + " ; ".join(failed)

    # ========================
    # 📦 MÉTADATA
    # ========================

    candidate["decision"] = decision
    candidate["decision_reason"] = reason

    candidate["baseline_average"] = baseline_avg
    candidate["candidate_average"] = candidate_avg
    candidate["baseline_min"] = baseline_min
    candidate["candidate_min"] = candidate_min
    candidate["adversarial_average"] = adversarial_avg

    # ========================
    # 📊 ENREGISTREMENT
    # ========================

    if decision in ["promote", "soft_promote"]:
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
        "adversarial_average": adversarial_avg
    }