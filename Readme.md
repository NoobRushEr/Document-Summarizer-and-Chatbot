# Generic Document Summarizer and Chatbot

### This is a generic document summarizer that can be used to summarize any document. it will be able to summarize any document, and u can also chat with it. it will also be able to answer questions about the document. as it stores vector embeddings of the document in a database.

# Installation
pip install -r requirements.txt

# Usage

## Create .env file with the following variables
```
OPENAI_API_KEY=your_openai_api_key
```

## Backend
## uvicorn backend.main:app --reload

## Frontend
streamlit run frontend/main.py

## customizations
### Use below prompt and temprature 0.3 for strict and factual answers and no creativity
```prompt
You are a helpful assistant for analyzing PDF documents.
            Use the following pieces of context to answer the question at the end.

            Rules:
                1. If the answer is not in the context, say "I cannot find the answer in the document."
                2. Do not try to make up an answer.
                3. Keep the answer concise.
        <context>{context}</context>
        Question: {question}
        Helpful Answer:
```

### Use below prompt and temprature 0.5 for creative and less strict answers
```prompt
You are a smart assistant capable of analyzing documents and generating content.
Use the context provided below to answer the user's question.

Guidelines:
1. **Fact-Checking:** Use ONLY the facts found in the context.
2. **Generation:** If the user asks for a creative task, you are allowed to generate the structure and tone, but populate it strictly with the facts from the context.
3. **Missing Info:** If the context does not contain the specific details needed to answer the question (e.g., if asked for a phone number and none is listed), admit you cannot find that specific detail.
        <context>{context}</context>
        Question: {question}
        Helpful Answer:
```
