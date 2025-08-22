# src/data_loader.py
import os
import textract
from pathlib import Path

class DataLoader:
    def __init__(self, input_dir="data/raw", output_file="data/combined_text.txt"):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_and_combine_files(self):
        combined_text = ""
        # Check if the input directory exists and has files
        if not self.input_dir.exists() or not os.listdir(self.input_dir):
            print(f"⚠️ Warning: Input directory '{self.input_dir}' is empty or does not exist.")
            # Create an empty output file and exit gracefully
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("")
            return

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                try:
                    print(f"📄 Reading... {filename}")
                    text = textract.process(file_path).decode("utf-8", errors="ignore")
                    combined_text += f"\n\n###{filename}###\n{text}"
                except Exception as e:
                    print(f"❌ Error while reading {filename}: {e}")

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f"✅ All files combined and saved to: {self.output_file}")
