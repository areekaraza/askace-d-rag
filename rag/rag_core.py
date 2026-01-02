"""Optimized RAG core with smart caching and fast retrieval"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    score: float


# Global index cache to avoid reloading
_INDEX_CACHE = {}


def _load_index_cached(storage_dir: str):
    """Load FAISS index with smart caching"""
    global _INDEX_CACHE
    
    storage_path = Path(storage_dir)
    index_path = storage_path / "faiss.index"
    meta_path = storage_path / "chunks.json"
    
    if not index_path.exists() or not meta_path.exists():
        raise RuntimeError("Index not found. Build index first.")
    
    # Cache key based on file modification times
    cache_key = f"{index_path.stat().st_mtime}_{meta_path.stat().st_mtime}"
    
    if cache_key not in _INDEX_CACHE:
        index = faiss.read_index(str(index_path))
        chunks = json.loads(meta_path.read_text(encoding="utf-8"))
        _INDEX_CACHE[cache_key] = (index, chunks)
        
        # Clear old cache entries (keep only latest)
        if len(_INDEX_CACHE) > 1:
            old_keys = list(_INDEX_CACHE.keys())[:-1]
            for key in old_keys:
                del _INDEX_CACHE[key]
    
    return _INDEX_CACHE[cache_key]


def get_cached_index(storage_dir: str):
    """Public interface for cached index loading"""
    return _load_index_cached(storage_dir)


def retrieve(
    *,
    question: str,
    storage_dir: str = "storage",
    top_k: int = 3,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    cache_func=None
) -> List[RetrievedChunk]:
    """Fast document retrieval with optimized search"""
    from rag.llm_client import embed_texts
    
    # Load index (cached)
    load_func = cache_func if cache_func else _load_index_cached
    index, chunks = load_func(storage_dir)
    
    # Generate query vector
    q_vec = np.array(embed_texts([question], model=embedding_model), dtype=np.float32)
    
    # Search (FAISS is already optimized)
    scores, ids = index.search(q_vec, min(top_k, len(chunks)))
    
    # Build results
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if 0 <= idx < len(chunks):
            chunk = chunks[idx]
            results.append(RetrievedChunk(
                text=chunk["text"],
                source=chunk.get("source", "unknown"),
                score=float(score)
            ))
    
    return results


def answer_with_rag(
    *,
    question: str,
    top_k: int = 3,
    storage_dir: str = "storage",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    chat_model: str = "llama3.2:1b",
    cache_func=None
) -> Tuple[str, List[RetrievedChunk]]:
    """Complete RAG pipeline with optimized context building"""
    from rag.llm_client import chat_answer
    
    # Retrieve relevant chunks
    retrieved = retrieve(
        question=question,
        storage_dir=storage_dir,
        top_k=top_k,
        embedding_model=embedding_model,
        cache_func=cache_func
    )
    
    if not retrieved:
        return "No relevant information found in the documents.", []
    
    # Build optimized context (limit total length)
    context_parts = []
    total_length = 0
    max_context = 800  # Reduced for speed
    
    for chunk in retrieved:
        chunk_text = f"[{chunk.source}] {chunk.text}"
        if total_length + len(chunk_text) > max_context:
            # Truncate last chunk to fit
            remaining = max_context - total_length
            if remaining > 50:  # Only add if substantial
                chunk_text = chunk_text[:remaining] + "..."
                context_parts.append(chunk_text)
            break
        
        context_parts.append(chunk_text)
        total_length += len(chunk_text)
    
    context = "\n\n".join(context_parts)
    
    # Generate answer
    answer = chat_answer(
        question=question,
        context=context,
        model=chat_model
    )
    
    return answer, retrieved
