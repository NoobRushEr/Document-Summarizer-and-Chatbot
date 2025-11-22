# Document Ingestion Script
# -------------------------
# This file handles loading and processing of documents.

# Implementation Checklist:
# 1. Define a function `ingest_document(file_path)`:
#    - Load the PDF using `PyPDFLoader`.
#    - Split the text into chunks using `RecursiveCharacterTextSplitter`.
#    - Initialize `OpenAIEmbeddings`.
#    - Store the chunks and embeddings in `ChromaDB` (persist it to disk).


import logging
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

logger = logging.getLogger(__name__)

CHROMA_DIR = "data/chroma"
os.makedirs(CHROMA_DIR, exist_ok=True)


def load_pdf(file_path: str):
    reader = PdfReader(file_path)
    docs = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        docs.append(
            Document(page_content=text, metadata={"page": i, "source": file_path})
        )
    return docs


def ingest_document(file_path: str):
    try:
        """Ingest a PDF document and store its embeddings in ChromaDB."""
        # Load the PDF document
        docs = load_pdf(file_path)

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(docs)

        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()

        # Store the chunks and embeddings in ChromaDB
        chroma_client = Chroma(
            persist_directory="data/chroma", embedding_function=embeddings
        )
        chroma_client.add_documents(chunks)

        logger.info("Ingested %d chunks from %s", len(chunks), file_path)
        return {"success": True, "chunks": len(chunks), "source": file_path}
    except Exception as e:
        logger.exception("Error ingesting document")
        return {"success": False, "error": str(e)}
