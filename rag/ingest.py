"""Optimized document ingestion with fast chunking and embedding"""
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Tuple
import numpy as np
import faiss


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str


def _find_documents(data_dir: Path) -> Iterable[Path]:
    """Find supported document types"""
    extensions = {".txt", ".md", ".pdf", ".docx"}
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def _read_pdf(path: Path) -> str:
    """Extract text from PDF with error handling"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        parts = []
        for i, page in enumerate(reader.pages, 1):
            if text := page.extract_text().strip():
                parts.append(f"[Page {i}] {text}")
        return "\n\n".join(parts)
    except Exception:
        return ""


def _read_docx(path: Path) -> str:
    """Extract text from DOCX with error handling"""
    try:
        from docx import Document
        doc = Document(str(path))
        parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(parts)
    except Exception:
        return ""


def _read_text_file(path: Path) -> str:
    """Read text file with encoding fallback"""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp1252", errors="ignore")


def read_document(path: Path) -> str:
    """Read document based on file extension"""
    suffix = path.suffix.lower()
    
    readers = {
        ".txt": _read_text_file,
        ".md": _read_text_file,
        ".pdf": _read_pdf,
        ".docx": _read_docx
    }
    
    reader = readers.get(suffix)
    return reader(path) if reader else ""


def chunk_text(text: str, *, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Fast text chunking with minimal overlap"""
    if not text or chunk_overlap >= chunk_size:
        return []
    
    # Clean text
    text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        if end >= len(text):
            break
            
        start = end - chunk_overlap
    
    return chunks


def build_chunks(data_dir: Path, *, chunk_size: int = 500, chunk_overlap: int = 50) -> Tuple[List[Chunk], int]:
    """Build chunks from all documents in directory"""
    chunks = []
    file_count = 0
    
    for file_path in _find_documents(data_dir):
        try:
            content = read_document(file_path)
            if content.strip():
                file_count += 1
                for piece in chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap):
                    chunks.append(Chunk(text=piece, source=file_path.name))
        except Exception:
            continue  # Skip problematic files
    
    return chunks, file_count


def ingest(
    *,
    data_dir: str | os.PathLike = "data",
    storage_dir: str | os.PathLike = "storage",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> dict:
    """Optimized document ingestion pipeline"""
    from rag.llm_client import embed_texts
    
    # Setup paths
    data_path = Path(data_dir)
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Build chunks
    chunks, file_count = build_chunks(
        data_path, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    if not chunks:
        raise RuntimeError(
            f"No documents found in '{data_path.resolve()}'. "
            f"Add .txt, .md, .pdf, or .docx files and retry."
        )
    
    # Generate embeddings in batches for memory efficiency
    batch_size = 32
    all_vectors = []
    texts = [c.text for c in chunks]
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vectors = embed_texts(batch, model=embedding_model)
        all_vectors.extend(vectors)
    
    # Create FAISS index
    vectors_array = np.array(all_vectors, dtype=np.float32)
    dim = vectors_array.shape[1]
    
    # Use IndexFlatIP for best accuracy with cosine similarity
    index = faiss.IndexFlatIP(dim)
    index.add(vectors_array)
    
    # Save index and metadata
    index_path = storage_path / "faiss.index"
    meta_path = storage_path / "chunks.json"
    
    faiss.write_index(index, str(index_path))
    
    chunk_data = [asdict(chunk) for chunk in chunks]
    meta_path.write_text(
        json.dumps(chunk_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    return {
        "chunks": len(chunks),
        "files": file_count,
        "dim": dim,
        "embedding_model": embedding_model,
        "index_path": str(index_path),
        "meta_path": str(meta_path)
    }
