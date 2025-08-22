# src/generator.py

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

genai.configure(api_key=google_api_key)

# Paths to stored FAISS index and metadata
INDEX_PATH = "data/vector_index/faiss_index.bin"
METADATA_PATH = "data/vector_index/metadata.pkl"

@st.cache_resource
class Generator:
    def __init__(self):
        # Embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

        # Free Gemini model
        self.llm = genai.GenerativeModel("gemini-1.5-flash")

        try:
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Error loading FAISS index or metadata: {e}")
            self.index = None
            self.metadata = []
    
    def is_probably_legal(self, question: str) -> bool:
        """
        Heuristic: check if question looks like legal context.
        """
        legal_keywords = [
            "law", "legal", "judgement", "ipc", "case", "act", "rights",
            "penalty", "section", "contract", "article", "bail",
            "petition", "tribunal", "court", "supreme court", "high court"
        ]
        pattern = r"\b(" + "|".join(legal_keywords) + r")\b"
        return bool(re.search(pattern, question.lower()))

    def retrieve_similar_chunks(self, query: str, top_k: int = 3):
        if self.index is None or not self.metadata:
            return []
            
        query_vector = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def generate_answer(self, question: str, top_k: int = 3) -> str:
        """
        Use PDF context always, warn if question seems non-legal.
        """
        context_chunks = self.retrieve_similar_chunks(question, top_k=top_k)
        if not context_chunks:
             return "⚠️ I could not find enough relevant information in the uploaded documents to answer that."

        context_text = "\n".join(context_chunks)
        
        prompt = f"""
        You are an Indian Legal Assistant.
        Use ONLY the given context from uploaded documents to answer.
        If the answer is not in the context, say:
        "I don't have enough legal information in the uploaded documents to answer that."

        Context:
        {context_text}

        Question:
        {question}
        """

        try:
            response = self.llm.generate_content(prompt)
            final_answer = response.text.strip()

            # Add a soft legal warning if it doesn't look legal
            if not self.is_probably_legal(question):
                final_answer += "\n\n⚠️ Note: Your question may not be directly legal, but I tried to answer using the uploaded documents."

            return final_answer
        except Exception as e:
            return f"⚠️ Error generating answer: {e}"
