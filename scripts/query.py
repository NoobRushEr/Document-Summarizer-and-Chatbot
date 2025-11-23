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

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)
load_dotenv()

# 1. Define a global variable to hold the chain, but start it as None
_cached_rag_chain = None


def get_rag_chain():
    """
    Initialize the chain ONLY if it hasn't been initialized yet.

    Returns:
        RetrievalQA: The initialized RetrievalQA chain.
    """
    global _cached_rag_chain

    # If we already loaded it, return it immediately
    if _cached_rag_chain is not None:
        return _cached_rag_chain

    print("Loading RAG models... (This happens only once)")
    try:
        embeddings = OpenAIEmbeddings()
        chroma_client = Chroma(
            persist_directory="data/chroma", embedding_function=embeddings
        )
        retriever = chroma_client.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20}
        )

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        prompt = PromptTemplate.from_template("""
            You are a smart assistant capable of analyzing documents and generating content.
            Use the context provided below to answer the user's question.

            Guidelines:
            1. **Fact-Checking:** Use ONLY the facts found in the context.
            2. **Generation:** If the user asks for a creative task, you are allowed to generate the structure and tone, but populate it strictly with the facts from the context.
            3. **Missing Info:** If the context does not contain the specific details needed to answer the question (e.g., if asked for a phone number and none is listed), admit you cannot find that specific detail.
        <context>{context}</context>
        Question: {question}
        Helpful Answer:
        """)

        # Save to the global variable
        _cached_rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )

        return _cached_rag_chain

    except Exception as e:
        logger.error(f"Error loading RAG: {e}")
        return None


def query_rag(question_text: str):
    """
    The main function you call from your other scripts.

    Args:
        question_text (str): The question to ask the RAG system.

    Returns:
        str: The answer to the question.
    """
    # 2. Get the chain (loads it if needed, reuses it if ready)
    chain = get_rag_chain()

    if not chain:
        return "System failed to initialize."

    try:
        response = chain.invoke({"query": question_text})
        return response["result"]
    except Exception as e:
        print(f"Error while querying RAG: {e}")
        return f"Error: {e}"
