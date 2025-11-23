# Frontend Application
# --------------------
# This file should contain the Streamlit user interface.

# Implementation Checklist:
# 1. Setup Streamlit page config.
# 2. Create a Sidebar:
#    - Add a file uploader widget for PDFs.
#    - When a file is uploaded, send a POST request to the Backend `/upload` endpoint.
# 3. Create a Main Chat Interface:
#    - Maintain chat history in `st.session_state`.
#    - Display previous messages.
#    - Add a chat input box.
#    - When user types a message, send a POST request to the Backend `/chat` endpoint.
#    - Display the response.

import logging

import requests
import streamlit as st

# Configuration
BACKEND_URL = "http://localhost:8000"
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Document Summarizer", layout="wide")
st.title("📄 Document Smart Assistant")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Helper Functions ---
def fetch_documents():
    """Ask backend for list of existing files."""
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.ok:
            return response.json().get("documents", [])
    except Exception:
        return []
    return []


def trigger_summarization(filename):
    """Send a summarization request for a specific file context."""
    # Add user intent to chat history
    prompt = f"Summarize the document: {filename}"
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(f"Summarizing {filename}..."):
        try:
            # We call the summarize endpoint (or chat endpoint with specific prompt)
            payload = {"question": prompt}
            response = requests.post(f"{BACKEND_URL}/chat", json=payload)

            if response.ok:
                data = response.json()
                ans = data.get("answer") or data.get("result")
                st.session_state.messages.append({"role": "assistant", "content": ans})
            else:
                st.error(f"Failed to summarize: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")


# --- Sidebar: Document Management ---
with st.sidebar:
    st.header("📂 Document Management")

    # 1. File Uploader
    st.subheader("Upload New")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload File"):
            with st.spinner("Uploading & Indexing..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if response.ok:
                        st.success("Uploaded Successfully!")
                        # Rerun to update the document list below
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    # 2. Existing Documents List
    st.subheader("Available Documents")

    # Fetch list from backend
    docs = fetch_documents()

    if not docs:
        st.info("No documents found. Upload one to get started.")
    else:
        for doc_name in docs:
            doc_name_ = " ".join(doc_name.split("_")[1:])
            # Create a container for the row
            col1, col2 = st.columns([4, 2.5])
            with col1:
                # Display shortened name to fit
                st.caption(f"📄 {doc_name_[:20]}...")
            with col2:
                # The Summarize Button
                if st.button(
                    "Summarize", key=f"btn_{doc_name_}", help=f"Summarize {doc_name_}"
                ):
                    trigger_summarization(doc_name)
                    st.rerun()

# --- Main Chat Interface ---

# 1. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # A. User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing documents..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat", json={"question": prompt}
                )

                if response.ok:
                    payload = response.json()
                    assistant_text = (
                        payload.get("answer") or payload.get("result") or "No answer."
                    )
                else:
                    assistant_text = f"Error: {response.status_code}"

            except requests.exceptions.ConnectionError:
                assistant_text = "Error: Backend not reachable."

            st.markdown(assistant_text)

    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
