# app.py
import os
from pathlib import Path
import streamlit as st

# Import pipeline modules
from src.data_loader import DataLoader
from src.text_cleaner import TextCleaner
from src.chunker import Chunker
from src.embedder import Embedder
from src.generator import Generator

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "user_uploaded"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_INDEX_DIR = PROJECT_ROOT / "data" / "vector_index"

for d in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Streamlit UI
st.set_page_config(page_title="Indian Legal Bot", page_icon="⚖️", layout="wide")
st.markdown("<h1 style='text-align:center;color:#ff6f00;'>⚖️ Indian Legal Bot</h1>", unsafe_allow_html=True)
st.write("Upload Indian legal files (PDF/DOCX/TXT) and then ask your legal questions.")

# Two-column layout
col1, col2 = st.columns([1, 2])

# -------- Left Panel (Upload & Processing) --------
with col1:
    st.subheader("📂 Upload & Process")
    uploaded_files = st.file_uploader("Upload legal files", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if uploaded_files:
        # Clear old files
        for folder in [UPLOAD_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_INDEX_DIR]:
            for f in folder.glob("*"):
                f.unlink()

        # Save uploaded files
        for up in uploaded_files:
            dest = UPLOAD_DIR / up.name
            with open(dest, "wb") as f:
                f.write(up.getbuffer())
        st.success("✅ Files uploaded!")

        try:
            with st.spinner("📂 Loading data..."):
                loader = DataLoader(input_dir=UPLOAD_DIR, output_file=RAW_DIR / "combined_text.txt")
                loader.load_and_combine_files()

            with st.spinner("✨ Cleaning text..."):
                cleaner = TextCleaner()
                cleaner.process()

            with st.spinner("✂️ Chunking text..."):
                chunker = Chunker()
                chunker.process()

            with st.spinner("🧠 Creating embeddings..."):
                embedder = Embedder()
                embedder.create_embeddings()

            st.success("✅ Documents processed and indexed!")

            if "gen" not in st.session_state:
                st.session_state.gen = Generator()

        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

# -------- Right Panel (Chat Interface) --------
with col2:
    st.subheader("💬 Legal Q&A")

    if "gen" in st.session_state:
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "👋 Welcome! Upload your legal docs on the left and then ask me questions here."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Type your legal question...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("⚖️ Thinking..."):
                    try:
                        answer = st.session_state.gen.generate_answer(prompt)
                    except Exception as e:
                        answer = f"Error generating answer: {e}"
                    st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.info("👈 Upload files first (left panel).")
