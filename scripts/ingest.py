# Document Ingestion Script
# -------------------------
# This file handles loading and processing of documents.

# Implementation Checklist:
# 1. Define a function `ingest_document(file_path)`:
#    - Load the PDF using `PyPDFLoader`.
#    - Split the text into chunks using `RecursiveCharacterTextSplitter`.
#    - Initialize `OpenAIEmbeddings`.
#    - Store the chunks and embeddings in `ChromaDB` (persist it to disk).

import os
from pypdf2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

logger = logging.getLogger(__name__)


def load_pdf(file_path: str):
    try:
        """Load a PDF document and return its text content."""
        reader = PdfReader(file_path)
        docs = []
        for i, page in enumerate(reader.pages, 1):
            docs.append({
                "page_content": page.extract_text() or "",
                "metadata": {"page": i}
            })  
        return docs
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return None

    


def ingest_document(file_path: str):
    try:
        """Ingest a PDF document and store its embeddings in ChromaDB."""
        # Load the PDF document
        docs = load_pdf(file_path)

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)

        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()

        # Store the chunks and embeddings in ChromaDB
        chroma_client = Chroma(persist_directory="data/chroma", embedding_function=embeddings)
        chroma_client.aadd_documents(chunks)

        # Persist the ChromaDB to disk
        chroma_client.persist()
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        return False
    else:
        logger.info(f"Document ingested successfully: {file_path}")
        return True