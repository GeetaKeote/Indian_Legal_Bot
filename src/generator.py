# src/generator.py

import os
import pickle
import faiss
import re
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import streamlit as st
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Disable GPU
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables
load_dotenv()

# Get API key (check Streamlit secrets first, fallback to .env)
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in Streamlit secrets or .env")

# Set environment variable so LangChain can pick it up
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Paths to stored FAISS index and metadata
INDEX_PATH = "data/vector_index/faiss_index.bin"
METADATA_PATH = "data/vector_index/metadata.pkl"

class Generator:
    def __init__(self):
        # Load embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2" ,  device="cpu")

        # Load FAISS index and metadata files directly
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")
        if not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

        self.index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            self.metadata = pickle.load(f)

        # Initialize the LLM and chain
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        self.prompt = self.get_prompt_template()
        self.chain = self.prompt | self.llm | StrOutputParser()

    def get_prompt_template(self):
        template = """
        You are an Indian Legal Assistant.
        Answer the question strictly based on the given context.
        If the answer is not in the context, say:
        "I don't have enough legal information to answer that."

        Context:
        {context}

        Question:
        {question}
        """
        return PromptTemplate.from_template(template)

    def is_legal_question(self, question: str, context_exists=True) -> bool:
        """
        Determine if a question is legal.
        If context (uploaded docs) exists, assume it's legal.
        Otherwise, fall back to keyword check.
        """
        if context_exists:
            return True  # trust uploaded legal docs

        legal_keywords = [
            "law", "legal", "judgement", "IPC", "case", "act", "rights", "penalty",
            "section", "contract", "article", "bail", "petition", "tribunal", "court"
        ]
        pattern = r"\b(" + "|".join(legal_keywords) + r")\b"
        return bool(re.search(pattern, question.lower()))

    def retrieve_similar_chunks(self, query, top_k=3):
        query_vector = self.embedding_model.encode([query])
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.metadata[idx])
        return results

    def generate_answer(self, question, top_k=3):
        # Step 1: Retrieve context
        context_chunks = self.retrieve_similar_chunks(question, top_k=top_k)
        context_text = "\n".join(context_chunks)

        # Step 2: Apply legal filter
        if not self.is_legal_question(question, context_exists=bool(context_chunks)):
            return "⚖️ I can only answer questions related to Indian law."

        if not context_text:
            return "I don't have enough legal information to answer that."

        # Step 3: Generate answer
        try:
            answer = self.chain.invoke({"context": context_text, "question": question})
            return answer
        except Exception as e:
            raise Exception(f"Error generating answer: {e}")
