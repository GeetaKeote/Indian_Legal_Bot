# app.py

import streamlit as st
from pathlib import Path
import os

# Import your pipeline modules
from src import data_loader, text_cleaner, chunker, embedder
from src.generator import Generator

# App title
st.set_page_config(page_title="⚖️ Indian Legal Bot", layout="wide")
st.title("⚖️ Indian Legal Bot")
st.write("Upload Indian legal documents (PDFs) on the left, then ask your questions here!")

# Sidebar for document upload
st.sidebar.header("📂 Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

# Paths
DATA_DIR = Path("data/raw")
CLEAN_PATH = Path("data/cleaned_text.txt")
CHUNK_PATH = Path("data/chunks.txt")
INDEX_DIR = Path("data/vector_index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Step 1: Save uploaded PDFs
if uploaded_files:
    for uploaded_file in uploaded_files:
        save_path = DATA_DIR / uploaded_file.name
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Files uploaded successfully!")
    with st.spinner("Processing documents..."):
    # Create an instance of the DataLoader class and run its method
        loader = data_loader.DataLoader(input_dir=str(DATA_DIR))
        loader.load_and_combine_files()

    # Create an instance of the TextCleaner class and run its method
    cleaner = text_cleaner.TextCleaner()
    cleaner.process()

    # Create an instance of the Chunker class and run its method
    chunker = chunker.Chunker()
    chunker.process()

    # Create an instance of the Embedder class and run its method
    embedder = embedder.Embedder()
    embedder.create_embeddings()

st.sidebar.success("✅ Documents processed and indexed!")
    # Step 2: Run pipeline
    #with st.spinner("Processing documents..."):
        #data_loader.run()    # Extract text from PDFs → combined_text.txt
       # text_cleaner.run()   # Clean text → cleaned_text.txt
       # chunker.run()        # Chunk text → chunks.txt
       # embedder.run()       # Create FAISS index → faiss_index + metadata.pkl
    #st.sidebar.success("✅ Documents processed and indexed!")

# Step 3: Initialize Generator
if "gen" not in st.session_state:
    try:
        st.session_state.gen = Generator()
    except Exception as e:
        st.error(f"Error initializing Generator: {e}")
        st.stop()

# Step 4: Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Ask a legal question..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = st.session_state.gen.generate_answer(prompt)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
