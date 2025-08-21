import os
import re
import argparse
from pathlib import Path

class TextCleaner:
    def __init__(self , input_file, output_file):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\t', ' ').replace('\f', '')
        text = re.sub(r'\n{2,}', "\n\n", text)
        return text.strip()
    
    def process(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_text = self.clean_text(raw_text)    

            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            
            print(f' Cleaned Text saved to: {self.output_file}')

        except Exception as e:
            print(f' Error processing file: {e}')
            raise  # Re-raise the exception to be caught by the parent process

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()
    
    cleaner = TextCleaner(args.input_file, args.output_file)
    cleaner.process()