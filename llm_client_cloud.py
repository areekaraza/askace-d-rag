import os
from functools import lru_cache
from typing import List

import requests


def embed_texts(
    texts: List[str],
    *,
    model: str = "text-embedding-3-small",
) -> List[List[float]]:
    """Use OpenAI embeddings for cloud deployment"""
    if not texts:
        return []
    
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Batch process for efficiency
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    
    return [data.embedding for data in response.data]


def chat_answer(
    *,
    question: str,
    context: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 150,
) -> str:
    """Use OpenAI chat for cloud deployment"""
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer briefly with citations:"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful document assistant. Answer using only the provided context."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.1,
    )

    return response.choices[0].message.content or ""