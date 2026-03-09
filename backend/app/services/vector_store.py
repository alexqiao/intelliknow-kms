import faiss
import numpy as np
import pickle
import os
from typing import List, Dict

class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        self.index_path = "data/faiss_index"
        os.makedirs(self.index_path, exist_ok=True)
        self.load()

    def add_vectors(self, embeddings: List[List[float]], chunks: List[str], doc_id: int) -> List[int]:
        vectors = np.array(embeddings).astype('float32')
        start_id = self.index.ntotal
        self.index.add(vectors)

        ids = []
        for i, chunk in enumerate(chunks):
            faiss_id = start_id + i
            self.metadata.append({"faiss_id": faiss_id, "content": chunk, "doc_id": doc_id})
            ids.append(faiss_id)

        self.save()
        return ids

    def search(self, query_vector: List[float], top_k: int = 5, intent: str = None) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        vector = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(vector, min(top_k * 2, self.index.ntotal))

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results[:top_k]

    def remove_document(self, doc_id: int):
        """Remove all vectors associated with a document by rebuilding the index"""
        if self.index.ntotal == 0:
            return

        # Filter metadata to keep only entries not matching doc_id
        kept_metadata = [m for m in self.metadata if m["doc_id"] != doc_id]

        if not kept_metadata:
            # All vectors removed, reset index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            self.save()
            return

        # Reconstruct vectors from old index
        vectors = []
        for m in kept_metadata:
            vector = self.index.reconstruct(int(m["faiss_id"]))
            vectors.append(vector)

        # Create new index and add vectors
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(vectors).astype('float32'))

        # Update metadata with new sequential faiss_ids
        self.metadata = []
        for i, m in enumerate(kept_metadata):
            self.metadata.append({
                "faiss_id": i,
                "content": m["content"],
                "doc_id": m["doc_id"]
            })

        self.save()

    def save(self):
        faiss.write_index(self.index, f"{self.index_path}/index.faiss")
        with open(f"{self.index_path}/metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        index_file = f"{self.index_path}/index.faiss"
        metadata_file = f"{self.index_path}/metadata.pkl"

        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
        if os.path.exists(metadata_file):
            with open(metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
