from pathlib import Path

def run():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    text_path = PROCESSED_DIR / "cleaned_text.txt"
    if not text_path.exists():
        print("⚠️ No cleaned_text.txt found.")
        return

    text = text_path.read_text(encoding="utf-8")

    # --- chunking logic ---
    words = text.split()
    chunk_size = 500
    chunks = [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

    with open(PROCESSED_DIR / "chunks.txt", "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk + "\n\n")

    print(f"✅ Chunking finished ({len(chunks)} chunks)")

if __name__ == "__main__":
    run()
