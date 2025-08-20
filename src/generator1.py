import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import pickle
import faiss
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Paths to stored FAISS index and metadata
INDEX_PATH = "data/vector_index/faiss_index.bin"
METADATA_PATH = "data/vector_index/metadata.pkl"

# Load FAISS index
index = faiss.read_index(INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

# Function to check if question is legal
def is_legal_question(question):
    legal_keywords = [
        "law", "legal", "judgement", "IPC", "case", "act", "rights", "penalty",
        "section", "contract", "article", "bail", "petition", "tribunal"
    ]
    pattern = r"\b(" + "|".join(legal_keywords) + r")\b"
    return bool(re.search(pattern, question.lower()))

# Retrieve similar chunks from FAISS
def retrieve_similar_chunks(query, top_k=3):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode([query])
    distances, indices = index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        if idx != -1:
            results.append(metadata[idx])
    return results

# Generate answer
def generate_answer(question, top_k=3):
    if not is_legal_question(question):
        return "I can only answer questions related to Indian law."

    context_chunks = retrieve_similar_chunks(question, top_k=top_k)
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

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()

# Wrapper function for app.py
def generate_answer_from_retriever(question, top_k=3):
    return generate_answer(question, top_k)

# Run loop if standalone
if __name__ == "__main__":
    while True:
        user_query = input("\nAsk a legal question (or type 'exit'): ")
        if user_query.lower() == "exit":
            break
        print("\nAI Answer:", generate_answer_from_retriever(user_query))
