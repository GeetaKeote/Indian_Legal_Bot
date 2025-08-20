# app.py

import streamlit as st
from pathlib import Path
import os
import shutil

# Import your pipeline modules
from src.data_loader import DataLoader
from src.text_cleaner import TextCleaner
from src.chunker import Chunker
from src.embedder import Embedder
from src.generator import Generator

# App title
st.set_page_config(page_title="⚖️ Indian Legal Bot", layout="wide")
st.title("⚖️ Indian Legal Bot")
st.write("Upload Indian legal documents (PDFs) on the left, then ask your questions here!")

# Paths
DATA_DIR = Path("data/raw")
CLEAN_PATH = Path("data/processed/cleaned_text.txt")
CHUNK_PATH = Path("data/processed/chunks.txt")
INDEX_DIR = Path("data/vector_index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)

# Step 1: Sidebar for document upload
st.sidebar.header("📂 Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

# Step 2: Handle uploaded PDFs and run the pipeline
if uploaded_files:
    # Clear existing files in the raw directory
    if DATA_DIR.exists():
        for file in os.listdir(DATA_DIR):
            os.remove(os.path.join(DATA_DIR, file))

    for uploaded_file in uploaded_files:
        save_path = DATA_DIR / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Files uploaded successfully!")

    # Run the data processing pipeline
    with st.spinner("Processing documents..."):
        try:
            loader = DataLoader(input_dir=str(DATA_DIR))
            loader.load_and_combine_files()
            
            cleaner = TextCleaner()
            cleaner.process()
            
            chunker = Chunker()
            chunker.process()
            
            embedder = Embedder()
            embedder.create_embeddings()
            
            # Use session state to track that the pipeline has run
            st.session_state["pipeline_run"] = True
            st.sidebar.success("✅ Documents processed and indexed!")
            # This reruns the app to initialize the generator with the new files
            st.experimental_rerun()  
        except Exception as e:
            st.sidebar.error(f"Error processing documents: {e}")

# Step 3: Initialize Generator only AFTER the pipeline has successfully run
if "gen" not in st.session_state and st.session_state.get("pipeline_run"):
    try:
        st.session_state.gen = Generator()
    except Exception as e:
        st.error(f"Error initializing Generator: {e}")
        st.stop()
elif "gen" not in st.session_state:
    st.info("Upload PDF documents on the left to get started.")

# Step 4: Chat interface (this part remains the same)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "gen" in st.session_state and prompt := st.chat_input("Ask a legal question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = st.session_state.gen.generate_answer(prompt)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})