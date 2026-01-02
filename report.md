# RAG Chatbot Report (CCP)

## 1. Objective
Build a simple RAG-based chatbot for course notes that can answer questions using retrieved context.

## 2. Architecture
1. Ingestion: read documents from `data/`, chunk with overlap
2. Embedding: OpenAI embeddings (`text-embedding-3-small`)
3. Vector store: FAISS index saved under `storage/`
4. Retrieval: cosine-similarity via normalized inner product + top-k selection
5. Generation: OpenAI chat model answers using only retrieved context and adds citations

## 3. Technology Stack
- Python, Streamlit (UI)
- OpenAI API (embeddings + chat)
- FAISS (vector similarity search)

## 4. How to run
See `README.md`.

## 5. Evaluation (demo)
- Add 3-10 lecture notes into `data/`
- Ask 5 queries
- Confirm citations appear and answers align with retrieved notes

## 6. Limitations / Future work
- Better PDF parsing, reranking, caching
- Metadata filters (topic/week), streaming responses
- Authentication for public deployments
