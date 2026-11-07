from pathlib import Path

from loom.utils import (
    BASELINE_PATH,
    GEMINI_INPUT_PRICE_PER_1M,
    GEMINI_OUTPUT_PRICE_PER_1M,
    REPORT_OUTPUT_PATH,
)


def write_baseline(results: list[dict]):
    path = Path(BASELINE_PATH)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Baseline\n\n")
        f.write(
            "Task 6. Run all questions from eval_questions.md through the Phase 0 pipeline "
            "and log three numbers per question. This file is the most important artifact "
            "in the project — everything later gets measured against it.\n\n"
        )
        f.write("| Q# | Quality (1-5) | Latency (s) | Cost ($) | Notes |\n")
        f.write("|----|---------------|-------------|----------|-------|\n")
        for entry in results:
            q = entry["question"]
            r = entry["result"]
            latency = f"{r['latency_s']:.2f}" if r["latency_s"] is not None else ""
            if r["input_tokens"] is not None and r["output_tokens"] is not None:
                cost = (
                    r["input_tokens"] / 1_000_000 * GEMINI_INPUT_PRICE_PER_1M
                    + r["output_tokens"] / 1_000_000 * GEMINI_OUTPUT_PRICE_PER_1M
                )
                cost = f"{cost:.6f}"
            else:
                cost = ""
            notes = (r["answer"] or r["error"] or "").replace("\n", " ").replace("|", "/")
            f.write(f"| {q['id']} |  | {latency} | {cost} | {notes} |\n")


def write_report(results: list[dict]):
    path = Path(REPORT_OUTPUT_PATH)
    with open(path, "w", encoding="utf-8") as f:
        for entry in results:
            q = entry["question"]
            f.write(f"## {q['id']}\n")
            f.write(f"question: {q['question']}\n\n")
            for r in entry["result"] or []:
                chunk = r["result"]
                f.write(f"- [{r['score']:.3f}] {chunk['name']} ({chunk['path']}:{chunk['start_line']}-{chunk['end_line']})\n")
            f.write("\n")
