import os
import fitz  # PyMuPDF
import docx2txt
from pathlib import Path

class DataLoader:
    def __init__(self, input_dir="data/raw", output_file="data/raw/combined_text.txt"):
        self.input_dir = input_dir
        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def extract_pdf(self, file_path):
        """Extract text from PDF using PyMuPDF."""
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"[PDF Error] {file_path}: {e}")
        return text

    def extract_docx(self, file_path):
        """Extract text from DOCX using docx2txt."""
        try:
            return docx2txt.process(file_path) or ""
        except Exception as e:
            print(f"[DOCX Error] {file_path}: {e}")
            return ""

    def extract_txt(self, file_path):
        """Read text file directly."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"[TXT Error] {file_path}: {e}")
            return ""

    def extract_fallback(self, file_path):
        """Fallback: Try textract for unknown formats."""
        try:
            return textract.process(file_path).decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[Fallback Error] {file_path}: {e}")
            return ""

    def load_and_combine_files(self):
        combined_text = ""

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                ext = filename.lower().split(".")[-1]
                text = ""

                print(f"📂 Reading {filename} ...")

                if ext == "pdf":
                    text = self.extract_pdf(file_path)
                elif ext in ["docx", "doc"]:
                    text = self.extract_docx(file_path)
                elif ext == "txt":
                    text = self.extract_txt(file_path)
                else:
                    text = self.extract_fallback(file_path)

                print(f"   ➡ Extracted {len(text)} characters.")

                if text.strip():
                    combined_text += f"\n\n###{filename}###\n{text}"
                else:
                    print(f"⚠ Warning: No text extracted from {filename}")

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f"\n✅ All files combined and saved to: {self.output_file}")

if __name__ == "__main__":
    loader = DataLoader()
    loader.load_and_combine_files()
