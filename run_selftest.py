from selftest import self_test
from generator import generate_answer
from judge import judge
from memory_manager import load_memory, save_memory

result = self_test(
    load_memory_fn=load_memory,
    save_memory_fn=save_memory,
    generate_answer_fn=generate_answer,
    judge_fn=judge
)

print("\n===== RÉSULTATS =====")
for r in result["results"]:
    print(f"{r['test']} → {r['score'].get('total', 0)}")

print("\n===== DIAGNOSTICS =====")
print(result["diagnostics"])