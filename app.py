import os
import sys
import shutil
import subprocess
import streamlit as st
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
UPLOAD_DIR = PROJECT_ROOT / "data" / "user_uploaded"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Indian Legal Bot", page_icon="⚖️", layout="wide")

# ----------------------------
# Header Section
# ----------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 15px; background-color:#f9f9f9; border-radius:12px; margin-bottom:20px;">
        <h1 style="color:#ff6f00; margin-bottom:5px;">⚖️ Indian Legal Bot</h1>
        <p style="font-size:18px; color:#333;">Your AI-powered Indian legal research assistant.<br>
        Upload judgments or legal documents and ask precise questions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Sidebar for file upload
# ----------------------------
st.sidebar.header("📂 Upload Legal Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload files (PDF, DOCX, TXT)", accept_multiple_files=True, type=["pdf", "docx", "txt"]
)

if uploaded_files:
    # Clear old uploads
    for f in UPLOAD_DIR.iterdir():
        try:
            f.unlink()
        except Exception:
            pass

    saved_paths = []
    for up in uploaded_files:
        dest = UPLOAD_DIR / up.name
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        saved_paths.append(dest)

    st.sidebar.success(f"✅ {len(saved_paths)} file(s) uploaded.")

    # Run pipeline
    py = sys.executable
    st.sidebar.info("⚙️ Processing documents...")
    with st.spinner("Building knowledge base..."):
        subprocess.run([py, str(SRC_DIR / "data_loader.py")], check=True)
        subprocess.run([py, str(SRC_DIR / "text_cleaner.py")], check=True)
        subprocess.run([py, str(SRC_DIR / "chunker.py")], check=True)
        subprocess.run([py, str(SRC_DIR / "embedder.py")], check=True)

    st.sidebar.success("✅ Documents processed successfully!")

# ----------------------------
# Right panel - Q&A
# ----------------------------
st.subheader("💬 Ask Your Legal Question")

try:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))

    from src.generator import Generator
    generator_instance = Generator()
except Exception as e:
    st.error(f"Error initializing Generator: {e}")
    st.stop()

# Chat-like input/output
question = st.text_input("Type your question here...")

if st.button("Get Answer", use_container_width=True):
    if not question.strip():
        st.warning("⚠️ Please type a question.")
    else:
        with st.spinner("🔎 Analyzing documents and generating answer..."):
            try:
                answer = generator_instance.generate_answer(question, top_k=3)

                st.markdown(
                    f"""
                    <div style="background-color:#f1f1f1; padding:15px; border-radius:12px; margin-top:15px;">
                        <h3 style="color:#2c3e50;">✅ Answer:</h3>
                        <p style="font-size:16px; color:#333;">{answer}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"Error generating answer: {e}")
