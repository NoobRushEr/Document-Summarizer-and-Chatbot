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
import shutil

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from scripts.ingest import ingest_document
from scripts.query import query_rag

logger = logging.getLogger(__name__)

app = FastAPI()


class QuestionPayload(BaseModel):
    question: str


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
        result = ingest_document(saved_path)

        return {"success": True, "answer": "Document processed", "result": result}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(payload: QuestionPayload = Body(...)):
    question = payload.question
    try:
        # Call the query function
        result = query_rag(question)

        answer_text = result if isinstance(result, str) else str(result)
        return {"success": True, "answer": answer_text}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize(payload: QuestionPayload = Body(...)):
    question = payload.question
    try:
        # Call the query function
        result = query_rag(question)
        answer_text = result if isinstance(result, str) else str(result)
        return {"success": True, "answer": answer_text}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return {"error": str(e)}
