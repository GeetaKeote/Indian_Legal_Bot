import os
import fitz  # PyMuPDF
import argparse
from pathlib import Path

class DataLoader:
    def __init__(self, input_dir, output_file):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_and_combine_files(self):
        combined_text = ""
        if not self.input_dir.exists() or not os.listdir(self.input_dir):
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("")
            return

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if filename.lower().endswith(".pdf"):
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                combined_text += f"\n\n###{filename}###\n{text}"
            elif filename.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_text += f"\n\n###{filename}###\n{f.read()}"
            # (DOCX support can be added if needed)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()

    loader = DataLoader(args.input_dir, args.output_file)
    loader.load_and_combine_files()
