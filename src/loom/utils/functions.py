from pathlib import Path

from .constants import EXCLUDED_FILES, picked_folder


def get_folder():    
    try:
        is_valid = picked_folder.exists() and picked_folder.is_dir()
        if is_valid:
            return picked_folder
        else:
            raise OSError("Folder not found")
    except OSError as e:
         print("Error when getting folder", e)



def get_repo():
    root = Path(get_folder())
    files = []
    for p in root.rglob("*.py"):
        relative = p.relative_to(root).as_posix()
        if relative in EXCLUDED_FILES:
            continue
        files.append(str(p))
    return files



def print_results(results:list):
    for r in results:
        chunk = r["result"]
        print(f"[{r['score']:.3f}] {chunk['name']:<20} {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}")

