# src/chunker.py
import os

class Chunker:
    def __init__(self, input_file="data/processed/cleaned_text.txt", output_file="data/processed/chunks.txt",
                 chunk_size=500, overlap=50):
        self.input_file = input_file
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.overlap = overlap
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def chunk_text(self, text):
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))
        return chunks

    def process(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = self.chunk_text(text)

            with open(self.output_file, "w", encoding="utf-8") as f:
                for chunk in chunks:
                    f.write(chunk + "\n\n")

            print(f"Total chunks created: {len(chunks)}")
            print(f"Chunks saved to: {self.output_file}")

        except Exception as e:
            print(f"Error during chunking: {e}")

if __name__ == "__main__":
    chunker = Chunker()
    chunker.process() # <- The corrected line with parentheses