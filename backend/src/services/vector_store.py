
import faiss
import os
import json
import numpy as np
import logging
from logging import getLogger
from src.settings import settings
from src.services.openai_client import get_openai

logger = getLogger(__name__)
logger.setLevel(logging.INFO)

class VectorStore:
    """
    A minimal disk‑persisted FAISS + JSON vector store.
    Stores vectors in a single IndexFlatL2 index and maps them to text & metadata.
    """
    def __init__(self):
        self.index_path = os.path.join(settings.vector_store_path, settings.faiss_index_file)
        self.meta_path = os.path.join(settings.vector_store_path, settings.metadata_file)
        self._ensure_storage_dir()
        self.index, self.metadata = self._load_or_init()

    def _ensure_storage_dir(self):
        os.makedirs(settings.vector_store_path, exist_ok=True)

    def _load_or_init(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            index = faiss.IndexFlatL2(1536)  # GPT‑4 / text‑embedding‑3‑large dimension
            metadata = []
        return index, metadata

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    # --------------------
    # Public API
    # --------------------
    def add_texts(self, texts: list[str], meta: list[dict]):
        if len(texts) == 0:
            return
        openai = get_openai()
        # Batch embeddings
        embeddings = []
        for i in range(0, len(texts), 20):
            batch = texts[i:i+20]
            resp = openai.embeddings.create(
                input=batch,
                model=settings.azure_openai_embedding_deployment
            )
            for d in resp.data:
                embeddings.append(d.embedding)
        emb_np = np.array(embeddings).astype("float32")
        self.index.add(emb_np)
        self.metadata.extend(meta)
        self.save()

    def similarity_search(self, query: str, k: int = 4) -> list[tuple[str, dict, float]]:
        openai = get_openai()
        emb = openai.embeddings.create(
            input=[query],
            model=settings.azure_openai_embedding_deployment
        ).data[0].embedding
        emb_np = np.array([emb]).astype("float32")
        distances, idxs = self.index.search(emb_np, k)
        results = []
        for dist, idx in zip(distances[0], idxs[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            text = meta["text"]
            results.append((text, meta, float(dist)))
        return results
