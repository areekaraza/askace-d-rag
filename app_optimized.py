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

# Create required directories
Path("data").mkdir(exist_ok=True)
Path("storage").mkdir(exist_ok=True)

# Title
st.title("AskAce: D'RAG")
st.caption("How can I help you with your notes today?")

# Optimized lazy loading with minimal imports
@st.cache_resource(show_spinner="⚡ Loading AI modules...")
def _load_rag_functions():
    """Load RAG functions only when needed"""
    from rag.ingest import ingest
    from rag.rag_core import answer_with_rag, get_cached_index
    return ingest, answer_with_rag, get_cached_index

# Pre-check index existence for faster UI
@st.cache_data(ttl=30)  # Cache for 30 seconds
def _check_index_exists():
    return (Path("storage") / "faiss.index").exists()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("🚀 **Ultra-Fast Setup**\n- Optimized for speed\n- Smart caching\n- Minimal resources")
    
    # Model selection (fastest first)
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.slider("📄 Documents", 2, 8, 3)
    with col2:
        chunk_size = st.slider("📝 Chunk size", 400, 1000, 500, step=100)
    
    chat_model = st.selectbox(
        "🤖 Chat Model",
        ["llama3.2:1b", "phi3:mini", "llama3.2:3b"],
        help="Smaller = faster"
    )
    
    embedding_model = st.selectbox(
        "🔤 Embedding Model", 
        ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L6-v2"]
    )
    
    st.divider()
    
    # Build index button
    if st.button("🚀 Build Index", type="primary", use_container_width=True):
        with st.spinner("Building lightning-fast search index..."):
            try:
                ingest, _, _ = _load_rag_functions()
                stats = ingest(
                    data_dir="data",
                    storage_dir="storage",
                    chunk_size=chunk_size,
                    chunk_overlap=50,
                    embedding_model=f"sentence-transformers/{embedding_model}"
                )
                st.success(f"✅ Indexed {stats['chunks']} chunks from {stats.get('files', 0)} files")
                st.cache_data.clear()  # Clear cache to refresh index status
                st.rerun()
            except Exception as e:
                st.error(f"❌ {str(e)}")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_resource.clear()
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with col2:
        if st.button("📊 Status", use_container_width=True):
            try:
                import requests
                resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
                models = resp.json().get("models", []) if resp.status_code == 200 else []
                index_exists = _check_index_exists()
                
                st.write("**Ollama:**", "✅" if models else "❌")
                st.write("**Index:**", "✅" if index_exists else "❌")
                if models:
                    st.write("**Models:**", len(models))
            except:
                st.write("**Ollama:** ❌ Not running")

# Main chat interface
index_ready = _check_index_exists()

if not index_ready:
    st.warning("📋 **Getting Started**")
    st.info("1. Add documents to `data/` folder\n2. Click '🚀 Build Index'\n3. Start chatting!")
    
    # File uploader for convenience
    with st.expander("📁 Upload Documents"):
        uploaded_files = st.file_uploader(
            "Choose files", 
            type=['txt', 'md', 'pdf', 'docx'],
            accept_multiple_files=True,
            help="Upload your documents here"
        )
        
        if uploaded_files:
            for file in uploaded_files:
                (Path("data") / file.name).write_bytes(file.getvalue())
            st.success(f"Uploaded {len(uploaded_files)} files!")
    st.stop()

st.markdown("### 💬 Chat")

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"📚 {len(msg['sources'])} Sources"):
                for src in msg["sources"]:
                    st.markdown(f"**{src['source']}** (score: {src['score']:.2f})")
                    st.write(src["text"][:150] + "..." if len(src["text"]) > 150 else src["text"])

# Chat input
if prompt := st.chat_input("Ask about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching and generating..."):
            try:
                _, answer_with_rag, get_cached_index = _load_rag_functions()
                
                answer, retrieved = answer_with_rag(
                    question=prompt,
                    top_k=top_k,
                    storage_dir="storage",
                    embedding_model=f"sentence-transformers/{embedding_model}",
                    chat_model=chat_model,
                    cache_func=get_cached_index
                )
                
                st.markdown(answer)
                sources = [{"source": r.source, "score": r.score, "text": r.text} for r in retrieved]
                
                with st.expander(f"📚 {len(sources)} Sources"):
                    for src in sources:
                        st.markdown(f"**{src['source']}** (score: {src['score']:.2f})")
                        st.write(src["text"][:150] + "..." if len(src["text"]) > 150 else src["text"])
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "sources": sources
                })
                
            except Exception as e:
                st.error(f"❌ {str(e)}")
                if "model" in str(e).lower():
                    st.info(f"💡 Run: `ollama pull {chat_model}`")
                elif "index" in str(e).lower():
                    st.info("💡 Click 'Build Index' first")