from lab.candidate_registry import add_promoted, add_rejected


PROMOTION_MARGIN = 0.75
MIN_SCORE_TOLERANCE = 2
MIN_ADVERSARIAL_AVG = 33


def decide_candidate(candidate, baseline_eval, candidate_eval):
    baseline_avg = baseline_eval["benchmark"]["diagnostics"]["overall_average"]
    candidate_avg = candidate_eval["benchmark"]["diagnostics"]["overall_average"]

    baseline_min = baseline_eval["benchmark"]["diagnostics"]["min_score"]
    candidate_min = candidate_eval["benchmark"]["diagnostics"]["min_score"]

    candidate_block_scores = candidate_eval["benchmark"]["diagnostics"]["by_block"]
    adversarial_avg = candidate_block_scores.get("adversarial", {}).get("average", 0)

    target_avg = baseline_avg + PROMOTION_MARGIN
    target_min = baseline_min - MIN_SCORE_TOLERANCE

    avg_ok = candidate_avg >= target_avg
    min_ok = candidate_min >= target_min
    adversarial_ok = adversarial_avg >= MIN_ADVERSARIAL_AVG

    decision = "reject"
    failed = []

    if not avg_ok:
        failed.append(
            f"moyenne insuffisante ({candidate_avg:.2f} < {target_avg:.2f})"
        )

    if not min_ok:
        failed.append(
            f"min_score trop bas ({candidate_min:.2f} < {target_min:.2f})"
        )

    if not adversarial_ok:
        failed.append(
            f"adversarial trop faible ({adversarial_avg:.2f} < {MIN_ADVERSARIAL_AVG:.2f})"
        )

    reason = "Candidat insuffisant"
    if failed:
        reason += " | " + " ; ".join(failed)

    if avg_ok and min_ok and adversarial_ok:
        decision = "promote"
        reason = "Candidat meilleur que la baseline sur le benchmark labo"

    candidate["decision_reason"] = reason
    candidate["baseline_average"] = baseline_avg
    candidate["candidate_average"] = candidate_avg
    candidate["baseline_min"] = baseline_min
    candidate["candidate_min"] = candidate_min
    candidate["adversarial_average"] = adversarial_avg

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
        "adversarial_average": adversarial_avg
    }
