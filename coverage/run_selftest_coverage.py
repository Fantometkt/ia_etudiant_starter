from coverage.selftest_coverage import self_test_coverage
from generator import generate_answer
from judge import judge
from memory_manager import load_memory, save_memory

print("=== DÉBUT SELFTEST COVERAGE ===")

result = self_test_coverage(
    load_memory_fn=load_memory,
    save_memory_fn=save_memory,
    generate_answer_fn=generate_answer,
    judge_fn=judge
)

print("=== SELFTEST COVERAGE TERMINÉ ===")

print("\n===== RÉSULTATS =====")
for r in result["results"]:
    print(f"{r['test']} → {r['score'].get('total', 0)}")

print("\n===== DIAGNOSTICS =====")
print(result["diagnostics"])