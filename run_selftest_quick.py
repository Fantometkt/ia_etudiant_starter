from selftest import self_test
from generator import generate_answer
from judge import judge
from memory_manager import load_memory, save_memory

print("=== DÉBUT SELFTEST QUICK ===")

result = self_test(
    load_memory_fn=load_memory,
    save_memory_fn=save_memory,
    generate_answer_fn=generate_answer,
    judge_fn=judge,
    test_mode="quick"
)

print("=== SELFTEST QUICK TERMINÉ ===")

print("\n===== RÉSULTATS DÉTAILLÉS =====")
for r in result["results"]:
    print("\n----------------------------------")
    print(f"TEST : {r['test']}")
    print(f"SCORE : {r['score'].get('total', 0)}")
    print(f"VERDICT : {r['score'].get('verdict', '')}")
    print(f"RISK FLAGS : {r['score'].get('risk_flags', [])}")
    print(f"WEAKNESS : {r['score'].get('main_weakness', '')}")
    print(f"HINT : {r['score'].get('improvement_hint', '')}")
    print(f"PREVIEW : {r['preview']}")

print("\n===== DIAGNOSTICS =====")
print(result["diagnostics"])