from loom.agent import Agent
from loom.eval import Evaluator
from loom.index import Vectorize
from loom.ingest import Chunker
from loom.utils import get_repo


def build():
    files = get_repo()
    vectorizer = Vectorize()
    chunker = Chunker(files_to_chunk=files, model=vectorizer.model)
    chunker.chunk_files()
    vectorizer.embed_chunks()


def search(query):
    Vectorize().search_vector(query)


def run_eval():
    Evaluator().evaluate_questions()


def run_baseline():
    Evaluator().evaluate_questions_llm()


def ask(question):
    result = Agent().answer(question)
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(result["answer"])


COMMANDS = {
    "build": build,
    "search": lambda: search(sys.argv[2]),
    "eval": run_eval,
    "baseline": run_baseline,
    "ask": lambda: ask(sys.argv[2]),
}

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python -m loom <{'|'.join(COMMANDS)}> [args]")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
