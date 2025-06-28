from src.services.vector_store import VectorStore
from src.models.chat import SourceReference
from src.services.web_search import BraveSearchService, SearchResult
from typing import List, Tuple


class RAGEngine:
    def __init__(self):
        self.store = VectorStore()
        self.last_used_sources: List[SourceReference] = []
        self.search_service = BraveSearchService()

    def augment_messages(self, messages: list[dict], include_web_search:bool=True) -> list[dict]:
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
        
        user_query = last_user["content"].strip()
        
        docs = self.store.similarity_search(user_query, k=4)
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

        # first condition is whether web search is enabled. second condition is subjective based on query.
        search_web = include_web_search and self._should_search_web(user_query, docs)

        # Add web search if needed
        if search_web:
            web_results = self.search_service.search(user_query, count=3)
            web_context = self._format_web_results(web_results)
            if web_context:
                context_snippets.append(f"Recent Web Information:\n{web_context}")
                
                # Track web sources
                for result in web_results:
                    web_source = SourceReference(
                        document_id=f"web_{result.url}",
                        filename=result.title,
                        page=0,
                        relevance_score=0.9,  # High relevance for recent web info
                        url=result.url,
                        source_type="web",
                        domain=result.domain,
                        description=result.description,
                        published_date=result.published_date
                    )
                    self.last_used_sources.append(web_source)
        
        if not context_snippets:
            return messages
        
        context_text = "\n---\n".join(context_snippets)
        sys_prompt = {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use the following context to answer the user's question. "
                "The context is from uploaded documents.\n\n"
                + (" and recent web search results" if search_web else "") + ".\n\n"
                f"Context:\n{context_text}\n\n"
                "When referencing information, please indicate whether it comes from "
                "uploaded documents or web sources."
            )
        }
        return [sys_prompt] + messages

    def _should_search_web(self, query: str, existing_docs: List[Tuple]) -> bool:
        """
        Decide whether to include web search based on query and existing results. 
        There are three main conditions:
        1. Query contains temporal keywords indicating need for recent information.
        2. Existing document results are insufficient (e.g., low confidence).
        3. Query relates to topics that typically require web search.
        """
        # Check for temporal keywords indicating need for recent info
        temporal_keywords = [
            'latest', 'recent', 'current', 'today', 'now', 'this year', 
            '2024', '2025', 'update', 'new', 'breaking', 'recently'
        ]
        
        has_temporal = any(keyword in query.lower() for keyword in temporal_keywords)
        
        # Check if existing document results seem insufficient
        low_document_confidence = not existing_docs or (
            len(existing_docs) > 0 and 
            all(distance > 0.8 for _, _, distance in existing_docs)  # High distance = low similarity
        )
        
        # Check for topics that typically need web search
        web_topics = [
            'news', 'weather', 'stock', 'price', 'market', 'election', 
            'policy', 'law', 'AI', 'web', 'internet'
        ]
        has_web_topic = any(topic in query.lower() for topic in web_topics)
        
        return has_temporal or low_document_confidence or has_web_topic

    def _format_web_results(self, results: List[SearchResult]) -> str:
        """Format web search results for context inclusion"""
        if not results:
            return ""
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result.title}\n"
                f"   {result.description}\n"
                f"   Source: {result.domain}"
            )
        
        return "\n\n".join(formatted)
    
    def document_only_search(self, messages: list[dict]) -> list[dict]:
        """
        Use only document search, no web search
        """
        return self.augment_messages(messages, include_web_search=False)

    def get_last_sources(self) -> List[SourceReference]:
        """Return the sources used in the last augment_messages call"""
        return self.last_used_sources.copy()
    
    def get_document_sources(self) -> List[SourceReference]:
        """Return only document sources from last search"""
        return [s for s in self.last_used_sources if not s.document_id.startswith("web_")]
    
    def get_web_sources(self) -> List[SourceReference]:
        """Return only web sources from last search"""
        return [s for s in self.last_used_sources if s.document_id.startswith("web_")]
