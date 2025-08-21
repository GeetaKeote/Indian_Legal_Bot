import os
import re
import streamlit as st
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the GOOGLE_API_KEY environment variable.
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file or set it in your environment.")

os.environ["GOOGLE_API_KEY"] = google_api_key

# Paths to stored FAISS index and metadata
INDEX_PATH = "data/vector_index/faiss_index.bin"
METADATA_PATH = "data/vector_index/metadata.pkl"

@st.cache_resource
class Generator:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        self.llm = genai.GenerativeModel("gemini-pro")

        try:
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Error loading FAISS index or metadata: {e}")
            self.index = None
            self.metadata = []
    
    def is_legal_question(self, question):
        legal_keywords = [
            "law", "legal", "judgement", "IPC", "case", "act", "rights", "penalty",
            "section", "contract", "article", "bail", "petition", "tribunal"
        ]
        pattern = r"\b(" + "|".join(legal_keywords) + r")\b"
        return bool(re.search(pattern, question.lower()))

    def retrieve_similar_chunks(self, query, top_k=3):
        if self.index is None or not self.metadata:
            return []
            
        query_vector = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results

    def generate_answer(self, question, top_k=3):
        if not self.is_legal_question(question):
            return "I can only answer questions related to Indian law."

        context_chunks = self.retrieve_similar_chunks(question, top_k=top_k)
        if not context_chunks:
             return "I don't have enough legal information to answer that based on the provided documents."

        context_text = "\n".join(context_chunks)
        
        prompt = f"""
        You are an Indian Legal Assistant.
        Answer the question strictly based on the given context.
        If the answer is not in the context, say:
        "I don't have enough legal information to answer that."

        Context:
        {context_text}

        Question:
        {question}
        """

        response = self.llm.generate_content(prompt)
        return response.text.strip()