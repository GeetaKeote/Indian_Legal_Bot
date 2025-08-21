import os
import faiss
import pickle
import argparse
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

class Embedder:
    def __init__(self, input_file, faiss_index_file, metadata_file):
        self.input_file = Path(input_file)
        self.faiss_index_file = Path(faiss_index_file)
        self.metadata_file = Path(metadata_file)
        self.faiss_index_file.parent.mkdir(parents=True, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def create_embeddings(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                documents = f.read().split("\n\n")

            embeddings = self.model.encode(documents, convert_to_numpy=True)
            embeddings = np.array(embeddings, dtype=np.float32)

            dimension = embeddings[0].shape[0]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)

            faiss.write_index(index, str(self.faiss_index_file))

            with open(self.metadata_file, "wb") as f:
                pickle.dump(documents, f)

            print(f" FAISS index saved to {self.faiss_index_file}")
            print(f" Metadata saved to {self.metadata_file}")

        except Exception as e:
            print(f"Error creating embeddings: {e}")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--faiss_index_file", type=str, required=True)
    parser.add_argument("--metadata_file", type=str, required=True)
    args = parser.parse_args()

    embedder = Embedder(args.input_file, args.faiss_index_file, args.metadata_file)
    embedder.create_embeddings()