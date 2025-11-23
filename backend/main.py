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


import hashlib
import json
import logging
import os
from typing import Optional

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scripts.ingest import ingest_document
from scripts.query import query_rag

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionPayload(BaseModel):
    question: str


class SummaryPayload(BaseModel):
    # Optional because for summarization we might not need a user question
    focus_area: Optional[str] = None


UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
META_FILE = os.path.join(UPLOAD_DIR, "upload_meta.json")


# load / persist metadata mapping {hash: {"filename": "<saved name>", "orig_name": "...", "path": "..."}}
def _load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_meta(m):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF file and return its metadata.

    Args:
        file (UploadFile): The PDF file to upload.

    Returns:
        dict: A dictionary containing the metadata of the uploaded file.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # read bytes (safe for typical PDF sizes; stream for huge files)
        contents = await file.read()
        file_hash = _sha256_bytes(contents)

        meta = _load_meta()
        if file_hash in meta:
            # Already uploaded — return existing metadata (no duplicate saved)
            existing = meta[file_hash]
            return {
                "success": True,
                "message": "file already uploaded",
                "file_info": existing,
            }

        # not found: persist using hash prefix to avoid collisions
        safe_name = f"{file_hash[:12]}_{os.path.basename(file.filename)}"
        saved_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(saved_path, "wb") as out:
            out.write(contents)

        # update meta
        meta[file_hash] = {
            "saved_name": safe_name,
            "orig_name": file.filename,
            "path": saved_path,
        }
        _save_meta(meta)

        await file.close()

        # Call the ingest function
        result = await run_in_threadpool(ingest_document, saved_path)

        return {"success": True, "message": "Document processed", "result": result}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(payload: QuestionPayload = Body(...)):
    """Chat with the document.

    Args:
        payload (QuestionPayload): The payload containing the question.

    Returns:
        dict: A dictionary containing the answer to the question.
    """
    try:
        # Call the query function
        answer = await run_in_threadpool(query_rag, payload.question)

        answer_text = answer if isinstance(answer, str) else str(answer)
        return {"success": True, "answer": answer_text}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize(payload: SummaryPayload = Body(default={})):
    try:
        if payload.focus_area:
            prompt = f"Summarize the documents, focusing specifically on: {payload.focus_area}"
        else:
            prompt = "Provide a comprehensive summary of the key points in the provided documents. Use bullet points."

        summary = await run_in_threadpool(query_rag, prompt)
        return {"success": True, "answer": summary}
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def list_documents():
    """Returns a list of uploaded filenames."""
    if not os.path.exists(UPLOAD_DIR):
        return []

    # Get all PDF files in the upload directory
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]

    # Return them (you might want to return simple names, not the hashed ones)
    # Here we try to return a cleaner list if you saved metadata,
    # but for simplicity, let's just return the filenames on disk.
    return {"documents": files}


@app.get("/health")
def health_check():
    return {"status": "ok"}
