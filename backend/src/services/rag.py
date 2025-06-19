from src.services.vector_store import VectorStore
from src.models.chat import SourceReference
from typing import List, Tuple


class RAGEngine:
    def __init__(self):
        self.store = VectorStore()
        self.last_used_sources: List[SourceReference] = []

    def augment_messages(self, messages: list[dict]) -> list[dict]:
        """
        Given chat history, pull relevant context for the last user message
        and prepend a system message with the context.
        Also tracks the sources used for later reference.
        """
        # Clear previous sources
        self.last_used_sources = []
        
        # find last user message
        last_user = next((m for m in reversed(messages) if m["role"] == "user"), None)
        if not last_user:
            return messages
        
        docs = self.store.similarity_search(last_user["content"], k=4)
        context_snippets = []
        
        # Process retrieved documents and track sources
        for text, metadata, distance in docs:
            context_snippets.append(text)
            
            # Create source reference
            source = SourceReference(
                document_id=metadata.get("document_id", "unknown"),
                filename=metadata.get("filename", "unknown.pdf"),
                page=metadata.get("page", 0),
                relevance_score=float(distance)
            )
            self.last_used_sources.append(source)
        
        if not context_snippets:
            return messages
        
        context_text = "\n---\n".join(context_snippets)
        sys_prompt = {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use the following context to answer the user's question. "
                "The context is from uploaded documents.\n\n"
                f"Context:\n{context_text}"
            )
        }
        return [sys_prompt] + messages

    def get_last_sources(self) -> List[SourceReference]:
        """Return the sources used in the last augment_messages call"""
        return self.last_used_sources.copy()
