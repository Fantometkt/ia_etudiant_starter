import os
import subprocess
import time
import statistics

from lab_selector import select_best, save_best


CANDIDATES_PER_BATCH = 5
EVOLUTION_ROUNDS = 3


def run_generation():
    print(f"=== Génération de {CANDIDATES_PER_BATCH} candidats ===")

    for i in range(CANDIDATES_PER_BATCH):
        try:
            subprocess.run(["python3", "lab_selftest.py"], check=True)
        except Exception as e:
            print(f"Erreur génération : {e}")


def run_selection():
    print("=== Sélection du meilleur ===")
    best = select_best()
    save_best(best)
    return best


def evolve():
    print("=== DÉBUT ÉVOLUTION ===")

    history_scores = []

    for round_idx in range(1, EVOLUTION_ROUNDS + 1):

        print(f"\n=== ROUND {round_idx} ===")

        run_generation()

        print("Attente fin des tests...")
        time.sleep(2)

        best = run_selection()

        if best:
            try:
                best_score = best["ranking"][0]["average"]
                history_scores.append(best_score)
            except Exception:
                pass

        if len(history_scores) >= 2:
            variance = statistics.variance(history_scores)
            print(f"Variance évolution : {round(variance,2)}")

            if variance < 0.5:
                print("⚠️ Faible évolution détectée → arrêt anticipé")
                break

    print("\n=== RÉSUMÉ ÉVOLUTION ===")
    print(f"Scores : {history_scores}")

    if history_scores:
        print(f"Best score final : {max(history_scores)}")

    print("=== FIN ÉVOLUTION ===")


if __name__ == "__main__":
    evolve()