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

# Ensure folders exist
for folder in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Indian Legal Bot", page_icon="⚖️", layout="wide")

# Centered Title
st.markdown("<h1 style='text-align:center;color:#ff6f00;'>⚖️ Indian Legal Bot</h1>", unsafe_allow_html=True)

# Left (Upload) / Right (Q&A) Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📂 Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF/DOCX/TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)

# Run pipeline if new files uploaded
if uploaded_files:
    # Clear old files
    for folder in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
        for f in folder.iterdir():
            try: f.unlink()
            except Exception: pass

    # Save uploaded
    for up in uploaded_files:
        dest = UPLOAD_DIR / up.name
        with open(dest, "wb") as f:
            f.write(up.getbuffer())

    py = sys.executable
    try:
        st.info("📂 Running Data Loader...")
        subprocess.run([py, str(SRC_DIR / "data_loader.py"),
                        "--input_dir", str(UPLOAD_DIR),
                        "--output_file", str(RAW_DIR / "combined_text.txt")], check=True)

        st.info("✨ Cleaning text...")
        subprocess.run([py, str(SRC_DIR / "text_cleaner.py"),
                        "--input_file", str(RAW_DIR / "combined_text.txt"),
                        "--output_file", str(PROCESSED_DIR / "cleaned_text.txt")], check=True)

        st.info("✂️ Chunking text...")
        subprocess.run([py, str(SRC_DIR / "chunker.py"),
                        "--input_file", str(PROCESSED_DIR / "cleaned_text.txt"),
                        "--output_file", str(PROCESSED_DIR / "chunked_text.txt")], check=True)

        st.info("🧠 Creating embeddings...")
        subprocess.run([py, str(SRC_DIR / "embedder.py"),
                        "--input_file", str(PROCESSED_DIR / "chunked_text.txt"),
                        "--faiss_index_file", str(VECTOR_INDEX_DIR / "faiss_index.bin"),
                        "--metadata_file", str(VECTOR_INDEX_DIR / "metadata.pkl")], check=True)

        st.success("✅ Documents processed & indexed successfully.")

    except subprocess.CalledProcessError as e:
        st.error(f"Pipeline failed: {e}")
        st.stop()

# Import Generator only after pipeline
try:
    sys.path.append(str(PROJECT_ROOT))
    from src.generator import Generator
    generator_instance = Generator()
except Exception as e:
    st.error(f"Error initializing Generator: {e}")
    generator_instance = None

# Q&A Section
with col2:
    st.subheader("💬 Ask Questions")
    question = st.text_input("Ask a legal question:")
    if st.button("Get Answer") and generator_instance:
        if not question.strip():
            st.warning("Please type a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    answer = generator_instance.generate_answer(question, top_k=3)
                    st.markdown("### ✅ Answer:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
