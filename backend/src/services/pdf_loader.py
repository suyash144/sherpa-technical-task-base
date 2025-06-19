
from typing import List
from pypdf import PdfReader
from src.settings import settings

def load_pdf(file_path: str) -> List[str]:
    """
    Extract text per page from a PDF file.
    """
    reader = PdfReader(file_path)
    pages_text = [p.extract_text() or "" for p in reader.pages]
    return pages_text

def chunk_text(text: str) -> List[str]:
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i+size])
    return chunks
