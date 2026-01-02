from __future__ import annotations

import os
from typing import List

from openai import OpenAI


def _client() -> OpenAI:
    # The OpenAI SDK reads OPENAI_API_KEY from env automatically,
    # but we fail early with a clearer message.
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set. Set it in PowerShell or Streamlit secrets.")
    return OpenAI()


def embed_texts(texts: List[str], *, model: str = "text-embedding-3-small") -> List[List[float]]:
    if not texts:
        return []
    c = _client()
    resp = c.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def chat_answer(
    *,
    question: str,
    context: str,
    model: str = "gpt-4o-mini",
) -> str:
    c = _client()

    system = (
        "You are a helpful course assistant. Answer using ONLY the provided context. "
        "If the answer is not in the context, say you don't know. "
        "Always include citations like [source]."
    )

    user = f"""CONTEXT:\n{context}\n\nQUESTION:\n{question}\n"""

    resp = c.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content or ""
