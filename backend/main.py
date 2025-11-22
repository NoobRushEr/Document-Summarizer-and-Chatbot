# Backend API Entry Point
# -----------------------
# This file should contain the FastAPI application definition.

# Implementation Checklist:
# 1. Initialize FastAPI app.
# 2. Define a POST endpoint `/upload`:
#    - Accept a file upload (PDF).
#    - Save the file temporarily.
#    - Call the `ingest_document` function from `scripts/ingest.py`.
# 3. Define a POST endpoint `/chat`:
#    - Accept a JSON body with a "question".
#    - Call the `query_rag` function from `scripts/query.py`.
#    - Return the answer.
