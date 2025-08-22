# app.py
import os
import sys
import subprocess
from pathlib import Path
import streamlit as st

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
UPLOAD_DIR = PROJECT_ROOT / "data" / "user_uploaded"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_INDEX_DIR = PROJECT_ROOT / "data" / "vector_index"

for d in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="⚖️ Indian Legal Bot", layout="wide")

# Layout: left (upload) | right (chat)
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📂 Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF/DOCX/TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if uploaded_files:
        for folder in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
            for f in folder.iterdir():
                f.unlink()

        for up in uploaded_files:
            dest = UPLOAD_DIR / up.name
            with open(dest, "wb") as f:
                f.write(up.getbuffer())

        py = sys.executable
        try:
            st.info("📂 Running data loader...")
            subprocess.run([py, str(SRC_DIR / "data_loader.py"), "--input_dir", str(UPLOAD_DIR), "--output_file", str(RAW_DIR / "combined_text.txt")], check=True)

            st.info("✨ Cleaning text...")
            subprocess.run([py, str(SRC_DIR / "text_cleaner.py"), "--input_file", str(RAW_DIR / "combined_text.txt"), "--output_file", str(PROCESSED_DIR / "cleaned_text.txt")], check=True)

            st.info("✂️ Chunking...")
            subprocess.run([py, str(SRC_DIR / "chunker.py"), "--input_file", str(PROCESSED_DIR / "cleaned_text.txt"), "--output_file", str(PROCESSED_DIR / "chunked_text.txt")], check=True)

            st.info("🧠 Creating embeddings...")
            subprocess.run([py, str(SRC_DIR / "embedder.py"), "--input_file", str(PROCESSED_DIR / "chunked_text.txt"), "--faiss_index_file", str(VECTOR_INDEX_DIR / "faiss_index.bin"), "--metadata_file", str(VECTOR_INDEX_DIR / "metadata.pkl")], check=True)

            st.success("✅ Processing complete!")

        except subprocess.CalledProcessError as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

with col2:
    st.header("⚖️ Indian Legal Bot")
    try:
        sys.path.append(str(PROJECT_ROOT))
        from src.generator import get_generator
        gen = get_generator()
    except Exception as e:
        st.error(f"Error initializing Generator: {e}")
        st.stop()

    question = st.text_input("Ask a legal question:")
    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    answer = gen.generate_answer(question)
                    st.markdown("### ✅ Answer:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
