import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from loom.utils import EMBEDDING_OUTPUT_PATH, OUTPUT_PATH


class Vectorize:
    def __init__(self):
        self.embeddings = None
        self.model =  SentenceTransformer("all-mpnet-base-v2")

    def __load_chunks(self)->list:
        try:
            text = Path(OUTPUT_PATH).read_text(encoding="utf-8")
            chunks = [json.loads(line) for line in text.splitlines() if line.strip()]
            return chunks
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    def embed_chunks(self):
        try:
            chunks = self.__load_chunks()
            embeddings = [self.model.encode(chunk["text"]) for chunk in chunks]
            np.save(EMBEDDING_OUTPUT_PATH, embeddings)

            print(embeddings)
            print(f"Embeddings Saved to: {OUTPUT_PATH}")

        except (FileNotFoundError, OSError) as e:
            print(f"Embedding Failed: {e}")


    def search_vector(self):
        pass 

