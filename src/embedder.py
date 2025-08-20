import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, input_file="data/processed/chunks.txt", 
                 faiss_index_file="data/vector_index/faiss_index.bin",
                 metadata_file="data/vector_index/metadata.pkl"):
        
        self.input_file = input_file
        self.faiss_index_file = faiss_index_file
        self.metadata_file = metadata_file
        os.makedirs(os.path.dirname(self.faiss_index_file), exist_ok=True)

        # Using a free Hugging Face embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  

    def create_embeddings(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                documents = f.read().split("\n\n")  # split by chunks

            # Create embeddings
            embeddings = self.model.encode(documents, convert_to_numpy=True)
            embeddings = np.array(embeddings, dtype=np.float32)

            # Save embeddings in FAISS
            dimension = embeddings[0].shape[0]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)

            faiss.write_index(index, self.faiss_index_file)

            # Save metadata (text chunks)
            with open(self.metadata_file, "wb") as f:
                pickle.dump(documents, f)

            print(f" FAISS index saved to {self.faiss_index_file}")
            print(f" Metadata saved to {self.metadata_file}")

        except Exception as e:
            print(f"Error creating embeddings: {e}")


if __name__ == "__main__":
    embedder = Embedder()
    embedder.create_embeddings()
