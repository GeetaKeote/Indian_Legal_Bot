import os 
import re

class TextCleaner:
    def __init__(self , input_file ="data/raw/combined_text.txt", output_file ="data/processed/cleaned_text.txt"):
        self.input_file = input_file
        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def clean_text(self , text):
        text = re.sub(r'\s+', ' ', text)  # Keep single spaces
        text = text.replace('\t',' ').replace('\f', '')    # remove tabs, form feeds
        text = re.sub(r'\n{2,}', "\n\n", text)              # fix multiple new lines 
        return text.strip()
    
    def process(self):
        try:
            with open(self.input_file, "r" , encoding="utf-8") as f:
                raw_text  = f.read()

            cleaned_text = self.clean_text(raw_text)    

            with open(self.output_file, "w" , encoding="utf-8") as f:
                f.write(cleaned_text)
            
            print(f' Cleaned Text saved to: {self.output_file}')

        except Exception as e:
            print(f' Error processing file: {e}')


if __name__ == "__main__":
    cleaner = TextCleaner()
    cleaner.process()
