import copy
import time
import traceback

import generator
from lab.benchmark_suite import run_lab_benchmark


def _patch_generator(candidate):
    generator.BASE_SYSTEM_PROMPT = candidate["base_system_prompt"]
    generator.MODE_INSTRUCTIONS = candidate["mode_instructions"]


def _restore_generator(original_base, original_modes):
    generator.BASE_SYSTEM_PROMPT = original_base
    generator.MODE_INSTRUCTIONS = original_modes


def _safe_run_benchmark(mem, generate_answer_fn, judge_fn):
    try:
        result = run_lab_benchmark(
            mem=mem,
            generate_answer_fn=generate_answer_fn,
            judge_fn=judge_fn
        )
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def _compute_global_score(bench_result):
    if not bench_result or "scores" not in bench_result:
        return 0

    scores = bench_result.get("scores", [])
    if not scores:
        return 0

    return sum(scores) / len(scores)


def _extract_risk_flags(bench_result):
    flags = []
    if not bench_result:
        return flags

    for case in bench_result.get("cases", []):
        flags.extend(case.get("risk_flags", []))

    return list(set(flags))


def evaluate_candidate(candidate, mem, generate_answer_fn, judge_fn):
    original_base = generator.BASE_SYSTEM_PROMPT
    original_modes = copy.deepcopy(generator.MODE_INSTRUCTIONS)

    start_time = time.time()

    try:
        _patch_generator(candidate)

        bench_mem = copy.deepcopy(mem)

        bench_exec = _safe_run_benchmark(
            mem=bench_mem,
            generate_answer_fn=generate_answer_fn,
            judge_fn=judge_fn
        )

        if not bench_exec["success"]:
            return {
                "candidate_id": candidate["id"],
                "status": "failed",
                "error": bench_exec["error"],
                "traceback": bench_exec.get("traceback", "")
            }

        bench_result = bench_exec["result"]

        global_score = _compute_global_score(bench_result)
        risk_flags = _extract_risk_flags(bench_result)

        duration = time.time() - start_time

        return {
            "candidate_id": candidate["id"],
            "status": "evaluated",
            "benchmark": bench_result,
            "global_score": round(global_score, 3),
            "risk_flags": risk_flags,
            "evaluation_time_sec": round(duration, 2)
        }

    finally:
        _restore_generator(original_base, original_modes)