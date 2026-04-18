import copy

import generator
from lab.benchmark_suite import run_lab_benchmark


def _patch_generator(candidate):
    generator.BASE_SYSTEM_PROMPT = candidate["base_system_prompt"]
    generator.MODE_INSTRUCTIONS = candidate["mode_instructions"]


def _restore_generator(original_base, original_modes):
    generator.BASE_SYSTEM_PROMPT = original_base
    generator.MODE_INSTRUCTIONS = original_modes


def evaluate_candidate(candidate, mem, generate_answer_fn, judge_fn):
    original_base = generator.BASE_SYSTEM_PROMPT
    original_modes = copy.deepcopy(generator.MODE_INSTRUCTIONS)

    try:
        _patch_generator(candidate)

        bench_mem = copy.deepcopy(mem)
        bench_result = run_lab_benchmark(
            mem=bench_mem,
            generate_answer_fn=generate_answer_fn,
            judge_fn=judge_fn
        )

        return {
            "candidate_id": candidate["id"],
            "status": "evaluated",
            "benchmark": bench_result
        }

    finally:
        _restore_generator(original_base, original_modes)