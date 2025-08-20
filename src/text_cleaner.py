from pathlib import Path
import re

def run():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    RAW_DIR = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    text_path = RAW_DIR / "combined_text.txt"
    if not text_path.exists():
        print("⚠️ No combined_text.txt found.")
        return

    text = text_path.read_text(encoding="utf-8")

    # --- your cleaning logic ---
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    (PROCESSED_DIR / "cleaned_text.txt").write_text(text, encoding="utf-8")
    print("✅ Text cleaning finished")

if __name__ == "__main__":
    run()
