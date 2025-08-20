import fitz  # PyMuPDF
import docx2txt
from pathlib import Path

def run():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    RAW_DIR = PROJECT_ROOT / "data" / "raw"
    UPLOAD_DIR = PROJECT_ROOT / "data" / "user_uploaded"
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    combined_text = ""

    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.suffix.lower() == ".pdf":
            doc = fitz.open(file_path)
            for page in doc:
                combined_text += page.get_text()
        elif file_path.suffix.lower() == ".docx":
            combined_text += docx2txt.process(file_path)
        elif file_path.suffix.lower() == ".txt":
            combined_text += file_path.read_text(encoding="utf-8", errors="ignore")

    (RAW_DIR / "combined_text.txt").write_text(combined_text, encoding="utf-8")
    print("✅ Data loading finished")

if __name__ == "__main__":
    run()
