"""Optimized LLM client for local embeddings and Ollama chat"""
import os
from functools import lru_cache
from typing import List
import numpy as np
import requests


@lru_cache(maxsize=1)
def _get_embedder(model_id: str):
    """Load and optimize embedding model (cached)"""
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer(model_id, device='cpu')
    model.eval()
    
    # Enable in-place operations for speed
    for module in model.modules():
        if hasattr(module, 'inplace'):
            module.inplace = True
    
    return model


def embed_texts(texts: List[str], *, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
    """Generate embeddings with optimized speed"""
    if not texts:
        return []
    
    embedder = _get_embedder(model)
    
    # Fast encoding with numpy normalization
    vectors = embedder.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=False  # Do manual normalization
    )
    
    # Manual L2 normalization (faster than model's)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / (norms + 1e-8)  # Avoid division by zero
    
    return vectors.tolist()


def chat_answer(
    *, 
    question: str, 
    context: str, 
    model: str = "llama3.2:1b", 
    max_tokens: int = 120
) -> str:
    """Generate answer using Ollama with optimized settings"""
    ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    
    # Concise prompt for faster generation
    prompt = f"Based on this context, answer briefly:\n\nContext: {context[:1200]}...\n\nQ: {question}\nA:"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": max_tokens,
            "top_k": 20,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_thread": 4  # Optimize for multi-core
        }
    }
    
    try:
        response = requests.post(
            f"{ollama_url.rstrip('/')}/api/generate",
            json=payload,
            timeout=45  # Reduced timeout
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama connection failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Chat generation failed: {str(e)}")
