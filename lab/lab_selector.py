import os
import json

REPORTS_DIR = "lab_reports"

def load_reports():
    reports = []
    for file in os.listdir(REPORTS_DIR):
        if file.endswith(".json"):
            path = os.path.join(REPORTS_DIR, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    reports.append(data)
            except:
                continue
    return reports


def score_candidate(report):
    # Score basé sur les métriques du juge
    return report.get("average_score", 0)


def select_best():
    reports = load_reports()

    if not reports:
        print("Aucun rapport trouvé.")
        return None

    best = None
    best_score = -1

    for r in reports:
        score = score_candidate(r)
        if score > best_score:
            best = r
            best_score = score

    print(f"Meilleur score : {best_score}")
    return best


def save_best(best):
    if not best:
        return

    with open("best_candidate.json", "w") as f:
        json.dump(best, f, indent=2)

    print("Meilleur candidat sauvegardé.")