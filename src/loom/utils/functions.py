from pathlib import Path

from .constants import EXCLUDED_FILES, picked_folder


def get_folder():
    if not picked_folder.exists():
        raise FileNotFoundError(f"Folder not found: {picked_folder}")
    if not picked_folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {picked_folder}")
    return picked_folder


def get_repo():
    root = Path(get_folder())
    files = []
    for p in root.rglob("*.py"):
        relative = p.relative_to(root).as_posix()
        if relative in EXCLUDED_FILES:
            continue
        files.append(str(p))
    return files


def print_results(results: list):
    for r in results:
        chunk = r["result"]
        print(
            f"[{r['score']:.3f}] {chunk['name']:<20} {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}"
        )
