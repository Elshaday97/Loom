import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from loom.utils import EMBEDDING_OUTPUT_PATH, OUTPUT_PATH, print_results


class Vectorize:
    def __init__(self):
        self.embeddings: np.ndarray = None
        self.chunks: list[str] = None
        self.model =  SentenceTransformer("all-mpnet-base-v2")

    def __load_chunks(self)->list:
        try:
            text = Path(OUTPUT_PATH).read_text(encoding="utf-8")
            chunks = [json.loads(line) for line in text.splitlines() if line.strip()]
            self.chunks = chunks
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    def embed_chunks(self):
        try:
            if self.chunks is None:
                self.__load_chunks()

            embeddings = [self.model.encode(chunk["text"]) for chunk in self.chunks]
            np.save(EMBEDDING_OUTPUT_PATH, embeddings)
            self.embeddings = np.array(embeddings)
            print(f"Embeddings Saved to: {OUTPUT_PATH}")

        except (FileNotFoundError, OSError, TimeoutError, ConnectionError) as e:
            print(f"Embedding Failed: {e}")

    def __load_embeddings(self):
        try:
            embeddings = np.load(EMBEDDING_OUTPUT_PATH)
            self.embeddings = embeddings
            return embeddings
        except (FileNotFoundError, OSError) as e:
            print(f"Error Loading Embeddings: {e}")


    def __validate_bare_query(self, query):
        if not (query and isinstance(query, str)):
            raise TypeError("Query must be a string")
        query = query.strip()
        return query

    def __embed_query(self, query: str): 
        query_embedding = self.model.encode(query)

        if query_embedding is None:
            raise ValueError("Query Embedding can not be None")

        if query_embedding.shape[0] != self.model.get_embedding_dimension():
            raise ValueError("Invalid Dimension for Query")

        if not np.all(np.isfinite(query_embedding)):
            raise ValueError("Embedding contains NaN or Infinity")

        return query_embedding            

    def search_vector(self, bare_query: str, k_results: int = 5):
        try:
            query = self.__validate_bare_query(bare_query)
            
            if self.chunks is None:
                self.__load_chunks()

            if self.embeddings is None:
                self.__load_embeddings()

            query_embedding = self.__embed_query(query)
            score = self.embeddings @ query_embedding

            top_k_indices =np.argsort(score)[::-1][:k_results] 

            results = []
            for k in top_k_indices:
                results.append({"score": score[k], "result": self.chunks[k]})

            return results
            
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error Searching Vector For Query: {bare_query}: {e}")



