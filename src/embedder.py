from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
import faiss

def run():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    INDEX_DIR = PROJECT_ROOT / "data" / "index"
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    chunks_path = PROCESSED_DIR / "chunks.txt"
    if not chunks_path.exists():
        print("⚠️ No chunks.txt found.")
        return

    chunks = chunks_path.read_text(encoding="utf-8").split("\n\n")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=True)

    # Save FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "faiss_index.idx"))

    # Save chunks for retriever
    with open(INDEX_DIR / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Embedding finished and FAISS index saved")

if __name__ == "__main__":
    run()
