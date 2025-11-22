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
