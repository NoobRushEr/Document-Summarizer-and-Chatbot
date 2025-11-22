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


import logging
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

logger = logging.getLogger(__name__)


def query_rag(question: str):
    try:
        """Query the RAG system with a question and return the answer."""
        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()

        # Load the existing ChromaDB
        chroma_client = Chroma(persist_directory="data/chroma", embedding_function=embeddings)

        # Create a retriever from the DB
        retriever = chroma_client.as_retriever()

        # Initialize the LLM (e.g., ChatOpenAI)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

        # Create a RetrievalQA chain
        chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

        # Invoke the chain with the question and return the result
        result = chain.run(question)
        return result
    except Exception as e:
        logger.error(f"Error querying RAG: {e}")
        return None