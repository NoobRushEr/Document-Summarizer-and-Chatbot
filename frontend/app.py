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

# --- Sidebar (Kept as is) ---
st.sidebar.title("Upload Document")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    # Note: You might want to handle connection errors here with try/except
    try:
        response = requests.post("http://localhost:8000/upload", files=files)
        if response.ok:
            st.sidebar.success("Uploaded OK")
        else:
            st.sidebar.error(f"Upload failed: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")

# --- Chat Interface ---
st.sidebar.title("Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. Display existing history (Runs on every re-run)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Handle New Input
if prompt := st.chat_input("What is up?"):
    # A. Display User Message IMMEDIATELY
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # C. Generate Response (with a loading spinner)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat", json={"question": prompt}
                )

                if response.ok:
                    payload = response.json()
                    # Fallback logic for different API response keys
                    assistant_text = (
                        payload.get("answer")
                        or payload.get("result")
                        or "No answer provided."
                    )
                else:
                    assistant_text = f"Error: {response.status_code} - {response.text}"

            except requests.exceptions.ConnectionError:
                assistant_text = "Error: Could not connect to backend."

            # D. Display Assistant Message IMMEDIATELY
            st.markdown(assistant_text)

    # E. Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
