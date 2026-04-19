from collections import defaultdict

from lab.candidate_registry import load_promoted, load_rejected
from lab.lab_config import LAB_EVAL_VERSION


def _score(c):
    return c.get("candidate_decision_score", c.get("candidate_average", 0))


def _prompt_preview(c, max_len=220):
    txt = c.get("base_system_prompt", "") or ""
    txt = " ".join(txt.split())
    return txt[:max_len] + ("..." if len(txt) > max_len else "")


def _print_top(title, items, n=5):
    print(f"\n=== {title} ===")
    if not items:
        print("Aucun résultat.")
        return

    top_items = sorted(items, key=_score, reverse=True)[:n]
    for c in top_items:
        print("\n---")
        print(f"Score : {_score(c)}")
        print(f"Mutation : {c.get('mutation_label')}")
        print(f"Target : {c.get('target')}")
        print(f"Reason : {c.get('decision_reason', '')}")
        print("Prompt preview :")
        print(_prompt_preview(c))


def _print_stats_by_mutation(items):
    stats = defaultdict(list)
    for c in items:
        stats[c.get("mutation_label", "unknown")].append(_score(c))

    print("\n=== STATS PAR MUTATION ===")
    for k, vals in sorted(stats.items()):
        avg = sum(vals) / len(vals)
        print(f"{k} → avg={avg:.2f} | n={len(vals)}")


def main():
    promoted = [x for x in load_promoted() if x.get("eval_version") == LAB_EVAL_VERSION]
    rejected = [x for x in load_rejected() if x.get("eval_version") == LAB_EVAL_VERSION]
    all_items = promoted + rejected

    print("\n=== GLOBAL ===")
    print(f"Eval version : {LAB_EVAL_VERSION}")
    print(f"Promoted : {len(promoted)}")
    print(f"Rejected : {len(rejected)}")

    _print_top("TOP CANDIDATS", all_items, n=5)
    _print_stats_by_mutation(all_items)
    _print_top("PROMPTS QUI MARCHENT", promoted, n=5)


if __name__ == "__main__":
    main()
