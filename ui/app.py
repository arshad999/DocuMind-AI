import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from auth.auth import AuthManager
from storage.metadata_db import MetadataDB
from storage.vector_store import VectorStore
from ingestion.document_loader import DocumentLoader
from ingestion.chunking import Chunker
from ingestion.embedding import EmbeddingEngine
from llm.openai_client import OpenAIClient
from rag.retriever import Retriever
from rag.generator import DocumentGenerator
from utils.helpers import ensure_directory, safe_filename, text_to_docx, text_to_pdf
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
DB_DIR = DATA_DIR / "db"
VECTOR_DIR = DATA_DIR / "vector_store"

ensure_directory(DATA_DIR)
ensure_directory(UPLOAD_DIR)
ensure_directory(OUTPUT_DIR)
ensure_directory(DB_DIR)
ensure_directory(VECTOR_DIR)

AUTH_DB = DB_DIR / "auth.db"
META_DB = DB_DIR / "metadata.db"

auth_manager = AuthManager(AUTH_DB)
metadata_db = MetadataDB(META_DB)
openai_client = OpenAIClient()
embedding_engine = EmbeddingEngine(openai_client)
vector_store = VectorStore(VECTOR_DIR)
retriever = Retriever(vector_store, metadata_db, openai_client)
generator = DocumentGenerator(openai_client)

st.set_page_config(page_title="DocuMind AI", layout="wide")

SESSION_USER = "session_user"
SESSION_USER_ID = "session_user_id"

if SESSION_USER not in st.session_state:
    st.session_state[SESSION_USER] = None
    st.session_state[SESSION_USER_ID] = None


def rerun_app():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.stop()


def login_section():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if auth_manager.verify_user(username, password):
            st.session_state[SESSION_USER] = username.strip().lower()
            st.session_state[SESSION_USER_ID] = auth_manager.get_user_id(username)
            rerun_app()
        else:
            st.error("Invalid username or password.")


def signup_section():
    st.header("Sign up")
    username = st.text_input("Choose a username", key="signup_username")
    password = st.text_input("Choose a password", type="password", key="signup_password")
    if st.button("Create account"):
        success = auth_manager.create_user(username, password)
        if success:
            st.success("Account created. Please log in.")
        else:
            st.error("Unable to create account. Username may already exist.")


def upload_documents(user_id: int):
    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Select PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            sanitized = safe_filename(uploaded_file.name)
            destination = UPLOAD_DIR / str(user_id) / sanitized
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "wb") as f:
                f.write(uploaded_file.getbuffer())
            doc_data = DocumentLoader.load_document(destination)
            document_id = metadata_db.add_document(user_id, sanitized, str(destination), content_summary="".join(doc_data["headings"]))
            chunks = Chunker.split_text_into_chunks(doc_data["raw_text"])
            embeddings = embedding_engine.embed_chunks(chunks)
            vector_ids = []
            for i, chunk_text in enumerate(chunks):
                vector_id = metadata_db.add_chunk(user_id, document_id, chunk_text, None, i)
                vector_ids.append(vector_id)
            vector_store.add_vectors(user_id, embeddings, vector_ids)
        st.success("Upload complete and documents indexed.")


def show_library(user_id: int):
    st.header("Document Library")
    docs = metadata_db.get_user_documents(user_id)
    if not docs:
        st.info("You have no uploaded documents yet.")
        return
    for doc in docs:
        with st.expander(f"{doc['filename']} ({doc['uploaded_at']})"):
            st.write("**Path:**", doc["storage_path"])
            if doc["content_summary"]:
                st.write("**Summary:**", doc["content_summary"])


def generate_document(user_id: int):
    st.header("Generate Document")
    request = st.text_area("Draft prompt", height=120, placeholder="Create an employment agreement for India...")
    client_name = st.text_input("Client name (optional)")
    company_name = st.text_input("Company name (optional)")
    country = st.text_input("Country or jurisdiction (optional)")
    if st.button("Generate document"):
        if not request.strip():
            st.error("Please enter a draft prompt.")
            return
        optional_inputs = {
            "Client": client_name,
            "Company": company_name,
            "Country": country,
        }
        context_chunks = retriever.retrieve(user_id, request, top_k=6)
        output = generator.generate_document(context_chunks, request, optional_inputs)
        st.success("Document generated.")
        st.text_area("Generated document", value=output, height=320)

        filename_base = f"generated_{user_id}"
        docx_path = OUTPUT_DIR / f"{filename_base}.docx"
        pdf_path = OUTPUT_DIR / f"{filename_base}.pdf"
        text_to_docx(output, docx_path)
        text_to_pdf(output, pdf_path)

        with open(docx_path, "rb") as f:
            st.download_button("Download DOCX", f.read(), file_name=docx_path.name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f.read(), file_name=pdf_path.name, mime="application/pdf")


def main():
    st.title("DocuMind AI")
    if st.session_state[SESSION_USER] is None:
        tab = st.sidebar.radio("Account", ["Login", "Sign up"])
        if tab == "Login":
            login_section()
        else:
            signup_section()
    else:
        st.sidebar.write(f"Logged in as **{st.session_state[SESSION_USER]}**")
        if st.sidebar.button("Logout"):
            st.session_state[SESSION_USER] = None
            st.session_state[SESSION_USER_ID] = None
            rerun_app()

        page = st.sidebar.selectbox("App pages", ["Upload Documents", "Document Library", "Generate Document"])
        user_id = st.session_state[SESSION_USER_ID]
        if page == "Upload Documents":
            upload_documents(user_id)
        elif page == "Document Library":
            show_library(user_id)
        elif page == "Generate Document":
            generate_document(user_id)


if __name__ == "__main__":
    main()
