import re
from pathlib import Path

from loom.utils import (
    BASELINE_PATH,
    GEMINI_INPUT_PRICE_PER_1M,
    GEMINI_OUTPUT_PRICE_PER_1M,
    REPORT_OUTPUT_PATH,
)

_ROW_RE = re.compile(r"\|\s*(Q\d+)\s*\|")


def _format_row(entry: dict) -> str:
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
    return f"| {q['id']} |  | {latency} | {cost} | {notes} |\n"


def _load_existing_rows() -> dict[str, str]:
    path = Path(BASELINE_PATH)
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _ROW_RE.match(line)
        if match:
            rows[match.group(1)] = line + "\n"
    return rows


def succeeded_question_ids() -> set[str]:
    """Question IDs that already have a non-empty Cost ($) cell in baseline.md."""
    succeeded = set()
    for qid, line in _load_existing_rows().items():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[3]:
            succeeded.add(qid)
    return succeeded


def write_baseline(results: list[dict]):
    rows = _load_existing_rows()
    for entry in results:
        rows[entry["question"]["id"]] = _format_row(entry)

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
        for qid in sorted(rows, key=lambda x: int(x[1:])):
            f.write(rows[qid])


def write_report(results: list[dict]):
    path = Path(REPORT_OUTPUT_PATH)
    with open(path, "w", encoding="utf-8") as f:
        for entry in results:
            q = entry["question"]
            f.write(f"## {q['id']}\n")
            f.write(f"question: {q['question']}\n\n")
            for r in entry["result"] or []:
                chunk = r["result"]
                f.write(
                    f"- [{r['score']:.3f}] {chunk['name']} ({chunk['path']}:{chunk['start_line']}-{chunk['end_line']})\n"
                )
            f.write("\n")
