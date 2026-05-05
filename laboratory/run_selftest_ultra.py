import time

from selftest_ultra import self_test_ultra
from generator import generate_answer
from judge import judge
from memory_manager import load_memory, save_memory


def main():
    print("=== DÉBUT SELFTEST ULTRA ===", flush=True)

    start = time.time()

    result = self_test_ultra(
        load_memory_fn=load_memory,
        save_memory_fn=save_memory,
        generate_answer_fn=generate_answer,
        judge_fn=judge
    )

    duration = round(time.time() - start, 2)

    scores = [r["score"].get("total", 0) for r in result["results"]]
    avg = round(sum(scores) / len(scores), 2) if scores else 0

    print("=== SELFTEST ULTRA TERMINÉ ===", flush=True)
    print(f"Nombre total de tests : {len(result['results'])}", flush=True)
    print(f"Score moyen : {avg}", flush=True)
    print(f"Durée : {duration} sec", flush=True)

    print("\n===== DIAGNOSTICS =====", flush=True)
    print(result["diagnostics"], flush=True)

    print("\n===== RÉSULTATS =====", flush=True)
    for r in result["results"]:
        print(f"{r['test']} → {r['score'].get('total', 0)}", flush=True)


if __name__ == "__main__":
    main()