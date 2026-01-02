import os
from pathlib import Path
import streamlit as st

# Configure page
st.set_page_config(
    page_title="AskAce: D'RAG", 
    page_icon="🎯", 
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("AskAce: D'RAG")
st.caption("How can I help you with your notes today?")

# Ensure data directory exists immediately
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Ultra-lazy imports - only import when actually needed
@st.cache_resource(show_spinner="Loading AI modules...")
def get_ingest_func():
    from rag.ingest import ingest
    return ingest

@st.cache_resource(show_spinner="Loading chat engine...")
def get_answer_func():
    from rag.rag_core import answer_with_rag
    return answer_with_rag

@st.cache_data(show_spinner="Loading document index...")
def load_index_if_exists(storage_dir: str):
    storage_path = Path(storage_dir)
    if (storage_path / "faiss.index").exists():
        from rag.rag_core import get_cached_index
        return get_cached_index(storage_dir)
    return None, None

with st.sidebar:
    st.header("Settings")
    st.write("LLM:", "Ollama (local)")
    
    st.info("💡 **Speed Tips:**\n- Use smaller models (1b/3b)\n- Reduce top-k retrieval\n- Keep documents concise")

    top_k = st.slider("Top-k retrieval", min_value=2, max_value=10, value=3, step=1)  # Reduced default
    embedding_model = st.selectbox(
        "Embedding model",
        ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/paraphrase-MiniLM-L6-v2"],
        index=0
    )
    chat_model = st.selectbox(
        "Chat model", 
        ["llama3.2:1b", "phi3:mini", "llama3.2:3b", "qwen2.5:3b"],  # Fastest models first
        index=0,
        help="Make sure the model is pulled with: ollama pull <model-name>"
    )

    st.divider()
    if st.button("Build index", type="primary"):
        with st.spinner("Building search index..."):
            try:
                ingest = get_ingest_func()
                stats = ingest(
                    data_dir="data",
                    storage_dir="storage",
                    chunk_size=600,  # Even smaller for speed
                    chunk_overlap=50,  # Minimal overlap
                    embedding_model=embedding_model,
                )
                st.success(f"✅ Ready! {stats['chunks']} chunks from {stats.get('files', 'unknown')} files.")
                st.rerun()  # Refresh to enable chat
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if st.button("🗑️ Clear cache"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Cache cleared!")
        st.rerun()
    
    # Quick status check
    if st.button("📊 Check Status"):
        try:
            import requests
            resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
            models = resp.json().get("models", []) if resp.status_code == 200 else []
            index_exists = (Path("storage") / "faiss.index").exists()
            
            st.write("**Ollama:**", "✅ Running" if models else "❌ Not available")
            st.write("**Index:**", "✅ Ready" if index_exists else "❌ Missing - Build index first")
            if models:
                st.write("**Models:**", ", ".join([m.get('name', 'unknown') for m in models[:3]]))
        except:
            st.write("**Status:** ❌ Ollama not running")

# Check if system is ready
index_exists = (Path("storage") / "faiss.index").exists()

if not index_exists:
    st.warning("📋 **First time?** Add documents to `data/` folder and click 'Build index' above.")
    st.stop()

st.markdown("### 💬 Chat")

# Pre-load index for faster queries
index_data = load_index_if_exists("storage")

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
                    cache_func=load_index_if_exists,
                )
                st.markdown(answer)
                sources = [{"source": r.source, "score": r.score, "text": r.text} for r in retrieved]
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.markdown(f"**{source['source']}** (relevance: {source['score']:.2f})")
                        st.write(source["text"][:200] + "..." if len(source["text"]) > 200 else source["text"])
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
            except Exception as e:
                st.error(str(e))
                if "model" in str(e).lower() and "not found" in str(e).lower():
                    st.info(f"**Quick fix:** Run `ollama pull {chat_model}` in terminal")
                else:
                    st.caption("Check that Ollama is running with the selected model")
