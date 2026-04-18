import os
import subprocess
import time
from lab_selector import select_best, save_best

def run_generation():
    print("=== Génération de 3 candidats ===")
    subprocess.run(["python3", "lab_selftest.py"])


def run_selection():
    print("=== Sélection du meilleur ===")
    best = select_best()
    save_best(best)


def evolve():
    print("=== DÉBUT ÉVOLUTION ===")

    run_generation()

    print("Attente fin des tests...")
    time.sleep(2)

    run_selection()

    print("=== FIN ÉVOLUTION ===")


if __name__ == "__main__":
    evolve()