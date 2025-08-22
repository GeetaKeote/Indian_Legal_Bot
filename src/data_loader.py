# src/data_loader.py
import os
import argparse
from pathlib import Path
import fitz  # PyMuPDF for PDF
import docx  # python-docx for DOCX

class DataLoader:
    def __init__(self, input_dir, output_file):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def extract_pdf(self, filepath):
        text = ""
        try:
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text("text")
            doc.close()
        except Exception as e:
            print(f"Error reading PDF {filepath}: {e}")
        return text

    def extract_docx(self, filepath):
        text = ""
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {filepath}: {e}")
        return text

    def extract_txt(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT {filepath}: {e}")
            return ""

    def load_and_combine_files(self):
        combined_text = ""
        if not self.input_dir.exists() or not os.listdir(self.input_dir):
            print(f"Warning: Input directory '{self.input_dir}' is empty or missing.")
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("")
            return

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                ext = filename.lower().split(".")[-1]
                text = ""
                if ext == "pdf":
                    text = self.extract_pdf(file_path)
                elif ext == "docx":
                    text = self.extract_docx(file_path)
                elif ext == "txt":
                    text = self.extract_txt(file_path)
                else:
                    print(f"Unsupported file
