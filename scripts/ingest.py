# Document Ingestion Script
# -------------------------
# This file handles loading and processing of documents.

# Implementation Checklist:
# 1. Define a function `ingest_document(file_path)`:
#    - Load the PDF using `PyPDFLoader`.
#    - Split the text into chunks using `RecursiveCharacterTextSplitter`.
#    - Initialize `OpenAIEmbeddings`.
#    - Store the chunks and embeddings in `ChromaDB` (persist it to disk).
