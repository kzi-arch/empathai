"""RAG opsional. Gagal total tidak boleh menjatuhkan aplikasi."""
from __future__ import annotations

import logging
from functools import lru_cache

from empath.config import settings

log = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self) -> None:
        self._store = None
        self.available = False
        self._init()

    def _init(self) -> None:
        try:
            from langchain_chroma import Chroma
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,      # ← gemini-embedding-001
                google_api_key=settings.gemini_api_key,
                output_dimensionality=settings.embedding_dim,
                task_type="RETRIEVAL_QUERY",
            )
            self._store = Chroma(
                collection_name="psikologi",
                embedding_function=embeddings,
                persist_directory=str(settings.rag_persist_dir),
            )
            self.available = True
        except Exception:
            log.exception("knowledge base tidak tersedia, lanjut tanpa RAG")

    def retrieve(self, query: str) -> list[str]:
        if not self.available or self._store is None:
            return []
        try:
            hits = self._store.similarity_search_with_relevance_scores(
                query, k=settings.rag_k * 2
            )
        except Exception:
            log.exception("retrieval gagal")
            return []
        return [
            doc.page_content
            for doc, score in hits
            if score >= settings.rag_score_threshold
        ][: settings.rag_k]


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()