# RAG Query Script
# ----------------
# This file handles retrieving information and generating answers.

# Implementation Checklist:
# 1. Define a function `query_rag(question)`:
#    - Initialize `OpenAIEmbeddings`.
#    - Load the existing `ChromaDB`.
#    - Create a Retriever from the DB.
#    - Initialize the LLM (e.g., `ChatOpenAI`).
#    - Create a `RetrievalQA` chain.
#    - Invoke the chain with the question and return the result.
