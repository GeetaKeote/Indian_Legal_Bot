# src/data_loader.py
import os
import textract
import argparse
from pathlib import Path

class DataLoader:
    def __init__(self, input_dir, output_file):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_and_combine_files(self):
        combined_text = ""
        # Check if the input directory exists and has files
        if not self.input_dir.exists() or not os.listdir(self.input_dir):
            print(f"Warning: Input directory '{self.input_dir}' is empty or does not exist.")
            # Create an empty output file and exit gracefully
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write("")
            return

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path):
                try:
                    print(f'Reading...{filename}')
                    text = textract.process(file_path).decode('utf-8', errors='ignore')
                    combined_text += f"\n\n###{filename}###\n{text}"
                    
                except Exception as e:
                    print(f'Error While Reading File {filename}:{e}')

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f'\nAll files combined and saved to: {self.output_file}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loads and combines text from documents.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing input files.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the combined output text file.")
    args = parser.parse_args()

    loader = DataLoader(input_dir=args.input_dir, output_file=args.output_file)
    loader.load_and_combine_files()