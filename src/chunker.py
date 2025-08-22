import argparse
from pathlib import Path

class Chunker:
    def __init__(self, input_file, output_file, chunk_size=500, overlap=50):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def chunk_text(self, text):
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))
        return chunks

    def process(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = self.chunk_text(text)

        with open(self.output_file, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(chunk + "\n\n")

        print(f"✅ {len(chunks)} chunks saved to {self.output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()

    chunker = Chunker(args.input_file, args.output_file)
    chunker.process()
