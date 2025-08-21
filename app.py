import os
import sys
import shutil
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

# Ensure all necessary folders exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Indian Legal Bot", page_icon="⚖️", layout="centered")
st.markdown("<h1 style='text-align:center;color:#ff6f00;'>⚖️ Indian Legal Bot</h1>", unsafe_allow_html=True)
st.write("Upload 1-2 legal files (PDF / DOCX / TXT). The app will process them and let you ask questions about the uploaded data.")

uploaded_files = st.file_uploader("📂 Upload files (PDF, DOCX, TXT)", accept_multiple_files=True, type=["pdf", "docx", "txt"])

if uploaded_files:
    # Clear previous user uploads and data
    for folder in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
        if folder.exists():
            for f in folder.iterdir():
                try:
                    f.unlink()
                except Exception:
                    pass

    # Save uploaded files to the designated user_uploaded directory
    for up in uploaded_files:
        dest = UPLOAD_DIR / up.name
        with open(dest, "wb") as f:
            f.write(up.getbuffer())

    py = sys.executable
    
    # Run the pipeline scripts using subprocess, passing file paths as arguments
    try:
        st.info("📂 Running data loader...")
        subprocess.run([py, str(SRC_DIR / "data_loader.py"), "--input_dir", str(UPLOAD_DIR), "--output_file", str(RAW_DIR / "combined_text.txt")], check=True)

        st.info("✨ Cleaning text...")
        subprocess.run([py, str(SRC_DIR / "text_cleaner.py"), "--input_file", str(RAW_DIR / "combined_text.txt"), "--output_file", str(PROCESSED_DIR / "cleaned_text.txt")], check=True)

        st.info("✂️ Chunking text...")
        subprocess.run([py, str(SRC_DIR / "chunker.py"), "--input_file", str(PROCESSED_DIR / "cleaned_text.txt"), "--output_file", str(PROCESSED_DIR / "chunked_text.txt")], check=True)

        st.info("🧠 Creating embeddings & building FAISS index...")
        subprocess.run([py, str(SRC_DIR / "embedder.py"), "--input_file", str(PROCESSED_DIR / "chunked_text.txt"), "--faiss_index_file", str(VECTOR_INDEX_DIR / "faiss_index.bin"), "--metadata_file", str(VECTOR_INDEX_DIR / "metadata.pkl")], check=True)

        st.success("✅ Pipeline finished. Vector index and metadata are ready.")

    except subprocess.CalledProcessError as e:
        st.error(f"A script in the pipeline failed: {e}")
        st.stop()
    except FileNotFoundError as e:
        st.error(f"Required script or file not found: {e}")
        st.stop()
    
    # Import and instantiate the Generator class, which is now cached
    try:
        sys.path.append(str(PROJECT_ROOT))
        from src.generator import Generator
        generator_instance = Generator()

    except Exception as e:
        st.error(f"Error importing or initializing Generator: {e}")
        st.stop()
    
    st.info("Upload processing complete. Ask questions below about the uploaded documents.")

    question = st.text_input("💬 Ask a legal question about uploaded files:")
    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Retrieving context and generating answer..."):
                try:
                    answer = generator_instance.generate_answer(question, top_k=3)
                    st.markdown("### ✅ Answer:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
else:
    st.info("No files uploaded yet. Upload files to enable question answering.")
    st.write("Tip: upload 1 or 2 relevant legal judgments / law docs and then ask questions about them.")