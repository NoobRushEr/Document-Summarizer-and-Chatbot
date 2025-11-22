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

import logging
from fastapi import FastAPI, File, UploadFile
from scripts.ingest import ingest_document
from scripts.query import query_rag
import shutil

logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the file temporarily
        temp_file_path = f"temp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the ingest function
        result = ingest_document(temp_file_path)
        return {"message": "Document processed successfully", "result": result}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"error": str(e)}


@app.post("/chat")
async def chat(question: str):
    try:
        # Call the query function
        result = query_rag(question)
        return {"message": "Query processed successfully", "result": result}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"error": str(e)}


@app.post("/summarize")
async def summarize(question: str):
    try:
        # Call the query function
        result = query_rag(question)
        return {"message": "Query processed successfully", "result": result}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"error": str(e)}

