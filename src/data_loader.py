import os
import argparse
from pathlib import Path
from docx import Document
import fitz  # PyMuPDF for PDFs

class DataLoader:
    def __init__(self, input_dir, output_file):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_pdf(self, filepath):
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text("text")
        return text

    def load_docx(self, filepath):
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])

    def load_txt(self, filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def load_and_combine_files(self):
        combined_text = ""

        if not self.input_dir.exists() or not os.listdir(self.input_dir):
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("")
            return

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                try:
                    if filename.lower().endswith(".pdf"):
                        text = self.load_pdf(file_path)
                    elif filename.lower().endswith(".docx"):
                        text = self.load_docx(file_path)
                    elif filename.lower().endswith(".txt"):
                        text = self.load_txt(file_path)
                    else:
                        print(f"Skipping unsupported file: {filename}")
                        continue

                    combined_text += f"\n\n###{filename}###\n{text}"

                except Exception as e:
                    print(f"Error while reading {filename}: {e}")

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f"✅ All files combined into {self.output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()

    loader = DataLoader(args.input_dir, args.output_file)
    loader.load_and_combine_files()
