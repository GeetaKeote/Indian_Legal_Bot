import streamlit as st
from src import data_loader, text_cleaner, chunker, embedder, retriever, generator
from pathlib import Path

st.set_page_config(page_title="📘 Indian Legal Bot", layout="wide")

# --- Sidebar for file upload ---
st.sidebar.header("📂 Upload Legal Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF/DOCX/TXT files", type=["pdf", "docx", "txt"], accept_multiple_files=True
)

# --- Process uploaded files ---
if uploaded_files:
    UPLOAD_DIR = Path(__file__).resolve().parent / "data" / "user_uploaded"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for uploaded_file in uploaded_files:
        file_path = UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Files uploaded")

    # Run pipeline
    with st.spinner("🔄 Processing documents..."):
        data_loader.run()
        text_cleaner.run()
        chunker.run()
        embedder.run()
    st.sidebar.success("✅ Documents processed")

# --- Main chat UI ---
st.title("⚖️ Indian Legal Bot")
st.write("Welcome! Upload your legal documents on the left and ask me any questions below 👇")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask a legal question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generator.generate_answer(prompt)  # <- from your generator.py
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
