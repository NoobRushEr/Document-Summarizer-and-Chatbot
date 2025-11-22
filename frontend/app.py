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

logger = logging.getLogger(__name__)

st.title("Document Summarizer")

st.sidebar.title("Upload Document")

uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    # Send a POST request to the Backend `/upload` endpoint
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    response = requests.post("http://localhost:8000/upload", files=files)
    if response.ok:
        st.sidebar.success("Uploaded OK")
    else:
        st.sidebar.error(f"Upload failed: {response.text}")

st.sidebar.title("Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# chat
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send a POST request to the Backend `/chat` endpoint
    response = requests.post("http://localhost:8000/chat", json={"question": prompt})
    if response.ok:
        payload = response.json()
        assistant_text = payload.get("answer") or payload.get("result") or "No answer"
    else:
        assistant_text = f"Error: {response.status_code} {response.text}"

    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
