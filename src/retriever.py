# src/retriever.py
import os
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss

class Retriever:
    """
    Loads FAISS index + metadata and retrieves top-k relevant chunks for a query.
    """

    def __init__(self,
                 faiss_index_file="data/vector_index/faiss_index.bin",
                 metadata_file="data/vector_index/metadata.pkl",
                 model_name="all-MiniLM-L6-v2"):
        self.faiss_index_file = faiss_index_file
        self.metadata_file = metadata_file

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        # Load FAISS index
        if not os.path.exists(self.faiss_index_file):
            raise FileNotFoundError(f"FAISS index not found: {self.faiss_index_file}")

        self.index = faiss.read_index(self.faiss_index_file)

        # Load metadata (list of text chunks)
        if not os.path.exists(self.metadata_file):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")

        with open(self.metadata_file, "rb") as f:
            self.documents = pickle.load(f)  # expected: list of text chunks

    def embed_query(self, query):
        """
        Return numpy array embedding for a single query (shape: (d,))
        """
        emb = self.model.encode(query, convert_to_numpy=True)
        # ensure dtype float32 for FAISS
        if emb.dtype != np.float32:
            emb = emb.astype(np.float32)
        return emb

    def retrieve(self, query, top_k=5):
        """
        Returns list of dicts: [{"id": idx, "score": distance, "text": doc_text}, ...]
        """
        q_emb = self.embed_query(query).reshape(1, -1)
        distances, indices = self.index.search(q_emb, top_k)  # returns (1, k) arrays
        distances = distances[0].tolist()
        indices = indices[0].tolist()

        results = []
        for idx, dist in zip(indices, distances):
            if idx < 0:
                continue
            text = self.documents[idx] if idx < len(self.documents) else ""
            results.append({"id": int(idx), "score": float(dist), "text": text})
        return results


# quick test when run directly
if __name__ == "__main__":
    r = Retriever()
    q = "What is the punishment for contempt of court?"
    res = r.retrieve(q, top_k=3)
    for i, item in enumerate(res, 1):
        print(f"Result {i} | id={item['id']} | score={item['score']}")
        print(item["text"][:400])
        print("----")
