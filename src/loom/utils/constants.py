from pathlib import Path


def find_project_root(marker="pyproject.toml"):
    for parent in Path(__file__).resolve().parents:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"Could not find project root (no {marker} found above {__file__})")


DATA_ROOT_DIR=find_project_root() / "data"  
picked_folder = Path(DATA_ROOT_DIR) / "celery" / "celery"
chunk_file_name = "chunks.jsonl"
embedding_file_name = "embeddings.npy"
OUTPUT_PATH = Path(DATA_ROOT_DIR) / chunk_file_name
EMBEDDING_OUTPUT_PATH = Path(DATA_ROOT_DIR) / embedding_file_name
MAX_CHUNK_LINE = 50 # TODO: Revisit when choosing a model to understand token limit and adjust this threshold
EXCLUDED_FILES = {
    "backends/mongodb.py",
    "backends/dynamodb.py",
    "contrib/sphinx.py",
}

MAX_TOKEN_LIMIT=384
EVAL_QUESTIONS_PATH= find_project_root()/ "eval_questions.md"
REPORT_OUTPUT_PATH =find_project_root()/ "eval_report.md"
BASELINE_PATH = find_project_root() / "baseline.md"

# TODO: confirm current rate at ai.google.dev/pricing before trusting cost numbers
GEMINI_INPUT_PRICE_PER_1M = 0.75
GEMINI_OUTPUT_PRICE_PER_1M = 3.75

