import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not set in environment")

genai.configure(api_key=google_api_key)

INDEX_PATH = "data/vector_index/faiss_index.bin"
METADATA_PATH = "data/vector_index/metadata.pkl"

class Generator:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.llm = genai.GenerativeModel("gemini-pro")
        self.index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            self.metadata = pickle.load(f)

    def retrieve_similar_chunks(self, query, top_k=3):
        query_vector = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)
        return [self.metadata[idx] for idx in indices[0] if idx != -1]

    def generate_answer(self, question, top_k=3):
        # 🔹 Always include PDF context (no "legal keyword" blocking anymore)
        context_chunks = self.retrieve_similar_chunks(question, top_k=top_k)
        if not context_chunks:
            return "I don't have enough legal information to answer that."

        context_text = "\n".join(context_chunks)
        prompt = f"""
        You are an **Indian Legal Assistant**.
        Answer strictly based on the uploaded document context below.
        If not found, say: "I don't have enough legal information to answer that."

        Context from uploaded files:
        {context_text}

        Question:
        {question}
        """

        response = self.llm.generate_content(prompt)
        return response.text.strip()
