from loom.index import Vectorize
from loom.ingest import Chunker
from loom.utils import get_repo

files = get_repo()

def initialize():
    try:
        vectorizer = Vectorize()
        chunker = Chunker(files_to_chunk=files, model=vectorizer.model)
        chunker.chunk_files()
        vectorizer.embed_chunks()
    except (OSError, RuntimeError, ValueError) as e:
        print(f"Something went wrong: {e}")



if __name__ == '__main__':
    initialize()