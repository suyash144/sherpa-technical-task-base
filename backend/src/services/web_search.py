from src.settings import settings
from typing import List, Optional
import urllib.request
import urllib.parse
import urllib.error
import json
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    title: str
    url: str
    description: str
    published_date: Optional[str] = None
    domain: Optional[str] = None
    
    def __str__(self):
        return f"{self.title}: {self.description[:100]}..."


class BraveSearchService:  
    def __init__(self):  
        self.api_key = settings.brave_api_key  
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.timeout = 10
      
    def search(self, query: str, count: int = 5) -> List[SearchResult]:
        """
        Search the web using Brave Search API
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            
        Returns:
            List of SearchResult objects
        """
        if not self.api_key:
            logger.error("Brave API key not configured")
            return []
            
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []
            
        # Limit count to API maximum
        count = min(count, 20)
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query.strip(),
            "count": count,
            "safesearch": "moderate",
            "search_lang": "en-gb",
            "country": "GB",
            "freshness": "pw"  # Past week for fresher results
        }

        # Build URL with encoded parameters
        url_params = urllib.parse.urlencode(params)
        full_url = f"{self.base_url}?{url_params}"
        
        # Create request with headers
        request = urllib.request.Request(full_url)
        request.add_header("Accept", "application/json")
        request.add_header("X-Subscription-Token", self.api_key)
        
        try:
            logger.info(f"Searching Brave API for: {query}")
            
            # Make the request
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                # Check status code
                if response.getcode() != 200:
                    logger.error(f"Brave API error: {response.getcode()}")
                    return []
                
                # Read and parse JSON response
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
                return self._parse_results(data)
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("Brave API rate limit exceeded")
            elif e.code == 401:
                logger.error("Brave API authentication failed - check API key")
            else:
                logger.error(f"Brave API HTTP error: {e.code} - {e.reason}")
            return []
        except urllib.error.URLError as e:
            logger.error(f"Brave API connection error: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Brave API response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during Brave search: {str(e)}")
            return []
    
    def _parse_results(self, data: dict) -> List[SearchResult]:
        """Parse Brave API response into SearchResult objects"""
        results = []
        
        # Extract web results
        web_results = data.get("web", {}).get("results", [])
        
        for result in web_results:
            try:
                search_result = SearchResult(
                    title=result.get("title", "No title"),
                    url=result.get("url", ""),
                    description=result.get("description", "No description available"),
                    published_date=result.get("age"),
                    domain=self._extract_domain(result.get("url", ""))
                )
                
                # Only add results with valid URLs
                if search_result.url:
                    results.append(search_result)
                    
            except Exception as e:
                logger.warning(f"Failed to parse search result: {str(e)}")
                continue
                
        logger.info(f"Successfully parsed {len(results)} search results")
        return results
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
    
    def search_with_metadata(self, query: str, count: int = 5) -> dict:
        """
        Search and return results with additional metadata
        
        Returns:
            Dict with 'results', 'query', 'timestamp', and 'total_count'
        """
        results = self.search(query, count)
        
        return {
            "results": results,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_count": len(results),
            "success": len(results) > 0
        }
    
    def quick_search(self, query: str, max_results: int = 3) -> str:
        """
        Quick search that returns formatted string for immediate use
        
        Returns:
            Formatted string with search results
        """
        results = self.search(query, max_results)
        
        if not results:
            return f"No recent web results found for: {query}"
            
        formatted = f"Recent web results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result.title}**\n"
            formatted += f"   {result.description}\n"
            formatted += f"   Source: {result.domain} - {result.url}\n\n"
            
        return formatted
    