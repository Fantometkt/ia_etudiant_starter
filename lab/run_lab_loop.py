import argparse
import time

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

    for i in range(1, args.cycles + 1):
        result = run_real_lab_cycle(
            load_memory_fn=load_memory,
            generate_answer_fn=generate_answer,
            judge_fn=judge
        )

        print(
            f"[cycle {i}] "
            f"mutation={result['mutation_label']} | "
            f"target={result['target']} | "
            f"baseline={result['baseline_average']} | "
            f"candidate={result['candidate_average']} | "
            f"decision={result['decision']} | "
            f"reason={result['reason']}"
        )

        if i < args.cycles:
            time.sleep(args.sleep)

    print("=== FIN LAB LOOP RÉELLE ===")


if __name__ == "__main__":
    main()