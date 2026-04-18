import copy

from lab.benchmark_suite import run_lab_benchmark
from lab.candidate_generator import generate_candidate
from lab.candidate_registry import register_candidate
from lab.candidate_evaluator import evaluate_candidate
from lab.promotion_manager import decide_candidate


def run_real_lab_cycle(load_memory_fn, generate_answer_fn, judge_fn):
    mem = load_memory_fn()

    baseline_mem = copy.deepcopy(mem)
    baseline_benchmark = run_lab_benchmark(
        mem=baseline_mem,
        generate_answer_fn=generate_answer_fn,
        judge_fn=judge_fn
    )

    baseline_eval = {
        "benchmark": baseline_benchmark
    }

    candidate = generate_candidate()
    register_candidate(candidate)

    candidate_eval = evaluate_candidate(
        candidate=candidate,
        mem=mem,
        generate_answer_fn=generate_answer_fn,
        judge_fn=judge_fn
    )

    decision = decide_candidate(
        candidate=candidate,
        baseline_eval=baseline_eval,
        candidate_eval=candidate_eval
    )

    return {
        "candidate_id": candidate["id"],
        "mutation_label": candidate["mutation_label"],
        "target": candidate["target"],
        "baseline_average": baseline_benchmark["diagnostics"]["overall_average"],
        "candidate_average": candidate_eval["benchmark"]["diagnostics"]["overall_average"],
        "decision": decision["decision"],
        "reason": decision["reason"]
    }