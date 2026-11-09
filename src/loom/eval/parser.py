import re
from pathlib import Path

from loom.utils import EVAL_QUESTIONS_PATH


def parse_questions() -> list[dict]:
    path = Path(EVAL_QUESTIONS_PATH)
    text = path.read_text(encoding="utf-8")
    blocks = re.split(
        r"\n(?=## Q\d+)", text
    )  # split into one chunk per "## Qn" section

    questions = []
    for block in blocks:
        header_match = re.search(r"## (Q\d+)", block)
        question_match = re.search(r"-\s*question:\s*(.+?)\n-\s", block, re.DOTALL)
        if header_match and question_match:
            raw_question = question_match.group(1)
            clean_question = " ".join(
                line.strip() for line in raw_question.splitlines()
            )
            questions.append({"id": header_match.group(1), "question": clean_question})
    return questions
