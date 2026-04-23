import argparse
import time
import statistics

from memory_manager import load_memory
from generator import generate_answer
from judge import judge
from lab.loop_controller import run_real_lab_cycle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=10)
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    print("=== DÉBUT LAB LOOP RÉELLE ===")

    history_scores = []
    decisions = {"promote": 0, "soft_promote": 0, "reject": 0}

    best_score = -999
    best_baseline = None
    stagnation_counter = 0

    for i in range(1, args.cycles + 1):
        result = run_real_lab_cycle(
            load_memory_fn=load_memory,
            generate_answer_fn=generate_answer,
            judge_fn=judge
        )

        candidate_score = result.get("candidate_average", 0)
        baseline_score = result.get("baseline_average", 0)
        decision = result.get("decision", "unknown")
        reason = result.get("reason", "")

        history_scores.append(candidate_score)

        if decision in decisions:
            decisions[decision] += 1

        if candidate_score > best_score:
            best_score = candidate_score
            best_baseline = baseline_score
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        avg_score = round(sum(history_scores) / len(history_scores), 2)
        variance = (
            round(statistics.variance(history_scores), 2)
            if len(history_scores) > 1 else 0
        )

        delta_vs_baseline = round(candidate_score - baseline_score, 2)

        print(
            f"[cycle {i}] "
            f"mutation={result['mutation_label']} | "
            f"target={result['target']} | "
            f"score={candidate_score:.2f} | "
            f"baseline={baseline_score:.2f} | "
            f"delta={delta_vs_baseline:+.2f} | "
            f"best={best_score:.2f} | "
            f"avg={avg_score:.2f} | "
            f"var={variance:.2f} | "
            f"decision={decision}"
        )

        if reason:
            print(f"  ↳ reason: {reason}")

        if stagnation_counter >= 15:
            print("⚠️ STAGNATION DÉTECTÉE → arrêt anticipé")
            break

        if i < args.cycles:
            time.sleep(args.sleep)

    print("\n=== RÉSUMÉ FINAL ===")
    print(f"Cycles exécutés : {i}")
    print(f"Best score : {best_score}")
    if best_baseline is not None:
        print(f"Baseline du best : {best_baseline}")
        print(f"Delta best vs baseline : {round(best_score - best_baseline, 2):+.2f}")
    print(f"Score moyen : {avg_score}")
    print(f"Variance : {variance}")
    print(f"Décisions : {decisions}")
    print("=== FIN LAB LOOP RÉELLE ===")


if __name__ == "__main__":
    main()