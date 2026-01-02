import os
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="AskAce: D'RAG", page_icon="🎯")

st.title("AskAce: D'RAG")
st.caption("How can I help you with your notes today?")

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("🔑 **OpenAI API Key Required**")
    st.info("""
    **To deploy this app:**
    
    1. **Get OpenAI API Key:**
       - Go to [platform.openai.com](https://platform.openai.com)
       - Create account → API Keys → Create new key
    
    2. **Add to Streamlit Cloud:**
       - In your app dashboard, go to "Secrets"
       - Add: `OPENAI_API_KEY = "your-key-here"`
    
    3. **Or set environment variable locally:**
       ```
       export OPENAI_API_KEY=your-key-here
       ```
    """)
    st.stop()

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Ultra-lazy imports for cloud deployment
@st.cache_resource(show_spinner="Loading AI modules...")
def get_ingest_func():
    # Import cloud version of ingest that uses OpenAI embeddings
    import json
    import numpy as np
    import faiss
    from pathlib import Path
    from llm_client_cloud import embed_texts
    
    def ingest_cloud(data_dir="data", storage_dir="storage", chunk_size=600, chunk_overlap=50, embedding_model="text-embedding-3-small"):
        from rag.ingest import build_chunks
        
        data_path = Path(data_dir)
        storage_path = Path(storage_dir)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        chunks, file_count = build_chunks(data_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            raise RuntimeError(f"No documents found in '{data_path.resolve()}'. Add files to data/ and retry.")
        
        texts = [c.text for c in chunks]
        vectors = embed_texts(texts, model=embedding_model)
        
        vecs = np.array(vectors, dtype=np.float32)
        dim = vecs.shape[1]
        index = faiss.IndexFlatIP(dim)
        
        faiss.normalize_L2(vecs)
        index.add(vecs)
        
        faiss.write_index(index, str(storage_path / "faiss.index"))
        (storage_path / "chunks.json").write_text(
            json.dumps([{"text": c.text, "source": c.source} for c in chunks], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return {"chunks": len(chunks), "files": file_count, "embedding_model": embedding_model}
    
    return ingest_cloud

@st.cache_resource(show_spinner="Loading chat engine...")
def get_answer_func():
    from llm_client_cloud import chat_answer, embed_texts
    import json
    import numpy as np
    import faiss
    from pathlib import Path
    
    def answer_with_rag_cloud(question, top_k=3, storage_dir="storage", embedding_model="text-embedding-3-small", chat_model="gpt-4o-mini", cache_func=None):
        # Load index
        storage_path = Path(storage_dir)
        index = faiss.read_index(str(storage_path / "faiss.index"))
        chunks = json.loads((storage_path / "chunks.json").read_text(encoding="utf-8"))
        
        # Search
        q_vec = np.array(embed_texts([question], model=embedding_model), dtype=np.float32)
        faiss.normalize_L2(q_vec)
        scores, ids = index.search(q_vec, top_k)
        
        # Build context
        context_parts = []
        for score, idx in zip(scores[0], ids[0]):
            if 0 <= idx < len(chunks):
                chunk = chunks[idx]
                context_parts.append(f"[source: {chunk.get('source', 'unknown')}]\n{chunk['text']}")
        
        context = "\n\n".join(context_parts)
        answer = chat_answer(question=question, context=context, model=chat_model)
        
        # Return retrieved chunks info
        retrieved = []
        for score, idx in zip(scores[0], ids[0]):
            if 0 <= idx < len(chunks):
                chunk = chunks[idx]
                retrieved.append({
                    "text": chunk["text"], 
                    "source": chunk.get("source", "unknown"), 
                    "score": float(score)
                })
        
        return answer, retrieved
    
    return answer_with_rag_cloud

with st.sidebar:
    st.header("Settings")
    st.write("LLM:", "OpenAI (Cloud)")
    
    st.success("☁️ **Cloud Ready:**\n- No local setup needed\n- Fast OpenAI responses\n- Auto-scaling")

    top_k = st.slider("Top-k retrieval", min_value=2, max_value=10, value=3, step=1)
    embedding_model = st.selectbox(
        "Embedding model",
        ["text-embedding-3-small", "text-embedding-ada-002"],
        index=0
    )
    chat_model = st.selectbox(
        "Chat model", 
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"],
        index=0,
        help="gpt-4o-mini is fastest and most cost-effective"
    )

    st.divider()
    if st.button("Build Index", type="primary"):
        with st.spinner("Building search index..."):
            try:
                ingest = get_ingest_func()
                stats = ingest(
                    data_dir="data",
                    storage_dir="storage", 
                    chunk_size=600,
                    chunk_overlap=50,
                    embedding_model=embedding_model,
                )
                st.success(f"✅ Ready! {stats['chunks']} chunks from {stats.get('files', 'unknown')} files.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if st.button("🗑️ Clear Cache"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Cache cleared!")
        st.rerun()

# Check if index exists
index_exists = (Path("storage") / "faiss.index").exists()

if not index_exists:
    st.warning("📋 **Getting Started:**")
    st.info("1. Upload documents to the `data/` folder\n2. Click 'Build Index' above\n3. Start chatting!")
    
    # File uploader for easy document upload
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=['txt', 'md', 'pdf', 'docx'],
        accept_multiple_files=True,
        help="Upload your documents here, then click 'Build Index'"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = data_dir / uploaded_file.name
            file_path.write_bytes(uploaded_file.getvalue())
        st.success(f"✅ Uploaded {len(uploaded_files)} files. Now click 'Build Index'!")
    
    st.stop()

st.markdown("### 💬 Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"**{source['source']}** (relevance: {source['score']:.2f})")
                    st.write(source["text"][:200] + "..." if len(source["text"]) > 200 else source["text"])

if question := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching and answering..."):
            try:
                answer_with_rag = get_answer_func()
                answer, retrieved = answer_with_rag(
                    question=question,
                    top_k=top_k,
                    storage_dir="storage",
                    embedding_model=embedding_model,
                    chat_model=chat_model,
                )
                st.markdown(answer)
                sources = retrieved
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.markdown(f"**{source['source']}** (relevance: {source['score']:.2f})")
                        st.write(source["text"][:200] + "..." if len(source["text"]) > 200 else source["text"])
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
            except Exception as e:
                st.error(str(e))
                if "api" in str(e).lower() or "openai" in str(e).lower():
                    st.info("💡 **Check your OpenAI API key and credits**")
                else:
                    st.caption("Check your OpenAI API configuration")