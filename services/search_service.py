"""Search service using DuckDuckGo (optimized for speed)."""

import logging
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import random
import re

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)


class SearchService:
    """Service for web search and content scraping using DuckDuckGo."""

    def __init__(self, config: Config):
        """Initialize search service."""
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "Required libraries not available. "
                "Install with: pip install requests beautifulsoup4"
            )

        self.config = config
        self.max_results = config.SEARCH_MAX_RESULTS
        self.region = config.SEARCH_REGION
        self.pages_to_scrape = config.SEARCH_PAGES_TO_SCRAPE
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        logger.info(f"🔍 SearchService initialized (DuckDuckGo)")
        logger.info(f"   Region: {self.region}")
        logger.info(f"   Max results: {self.max_results}")
        logger.info(f"   Pages to scrape: {self.pages_to_scrape}")

    def _get_random_user_agent(self) -> str:
        """Get random user agent."""
        return random.choice(self.user_agents)

    def _scrape_page_content(self, url: str) -> str:
        """
        Scrape text content from a web page (optimized).
        
        Args:
            url: URL to scrape
            
        Returns:
            Extracted text
        """
        try:
            logger.debug(f"   📄 Scraping: {url[:80]}...")
            
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru,en;q=0.9',
            }
            
            # Shorter timeout for faster response
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                element.decompose()
            
            # Find main content
            main_content = None
            for selector in ['article', 'main', '[role="main"]', '.content', '.post-content', '#content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body if soup.body else soup
            
            # Extract text
            text = main_content.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Reduced limit for faster processing
            max_length = 1500
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            logger.debug(f"      ✅ Scraped {len(text)} chars")
            return text
            
        except Exception as e:
            logger.warning(f"      ⚠️ Failed to scrape {url[:40]}: {str(e)[:50]}")
            return ""

    def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo HTML interface.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"🦆 DuckDuckGo search for: '{query}'")
            
            params = {
                'q': query,
                'kl': self.region,
            }
            
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru,en;q=0.9',
            }
            
            response = requests.post(
                'https://html.duckduckgo.com/html/',
                data=params,
                headers=headers,
                timeout=8
            )
            response.raise_for_status()
            
            logger.info(f"✅ Response: {response.status_code}, {len(response.text)} bytes")
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            result_divs = soup.find_all('div', class_='result')
            logger.info(f"   Found {len(result_divs)} result divs")
            
            for idx, result_div in enumerate(result_divs, 1):
                try:
                    link_elem = result_div.find('a', class_='result__a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    if not url or not url.startswith('http'):
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    if not title:
                        title = f"Result {idx}"
                    
                    snippet_elem = result_div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'number': len(results) + 1,
                        'title': title[:200],
                        'link': url,
                        'body': snippet
                    })
                    
                    logger.debug(f"   ✅ [{len(results)}] {title[:50]}...")
                    
                    if len(results) >= self.max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"   ⚠️ Error parsing result {idx}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"❌ DuckDuckGo search error: {e}")
            return []

    def _perform_search_sync(self, query: str) -> List[Dict[str, Any]]:
        """
        Synchronous search with optimized content scraping.
        
        Args:
            query: Search query
            
        Returns:
            List of results with scraped content
        """
        try:
            # Perform search
            results = self._search_duckduckgo(query)
            
            logger.info(f"✅ Found {len(results)} search results")
            
            # Scrape content from top N pages (in parallel for speed)
            if results and self.pages_to_scrape > 0:
                pages_to_scrape = min(len(results), self.pages_to_scrape)
                logger.info(f"🌐 Scraping top {pages_to_scrape} pages (parallel)...")
                
                # Use ThreadPoolExecutor for parallel scraping
                urls_to_scrape = [r['link'] for r in results[:pages_to_scrape]]
                
                with ThreadPoolExecutor(max_workers=pages_to_scrape) as executor:
                    scraped_contents = list(executor.map(self._scrape_page_content, urls_to_scrape))
                
                # Update results with scraped content
                for idx, content in enumerate(scraped_contents):
                    if content:
                        results[idx]['body'] = content
                
                logger.info(f"✅ Scraped {pages_to_scrape} pages")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Async search with content scraping.
        
        Args:
            query: Search query
            
        Returns:
            List of results with content
        """
        logger.info(f"🚀 Async search starting: '{query}'")
        
        loop = asyncio.get_event_loop()
        
        try:
            results = await loop.run_in_executor(
                self._executor,
                self._perform_search_sync,
                query
            )
            
            logger.info(f"✅ Search complete: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Async search error: {e}")
            return []

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format results for display."""
        if not results:
            return "🔍 Результаты не найдены."
        
        formatted = "🔍 Результаты поиска:\n\n"
        for result in results:
            formatted += f"{result['number']}. {result['title']}\n"
            formatted += f"🔗 {result['link']}\n\n"
        
        return formatted

    def format_search_context_for_llm(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Format results with content for LLM (with current date)."""
        if not results:
            return f"Поиск по запросу '{query}' не дал результатов."
        
        from datetime import datetime
        
        logger.info(f"📋 Formatting {len(results)} results for LLM")
        
        # Add current date/time to context
        current_date = datetime.now().strftime("%d.%m.%Y")
        current_time = datetime.now().strftime("%H:%M")
        
        context = f"=== ТЕКУЩАЯ ДАТА И ВРЕМЯ ===\n"
        context += f"Сегодня: {current_date}, время: {current_time} (московское время)\n\n"
        context += f"=== РЕЗУЛЬТАТЫ ПОИСКА: '{query}' ===\n\n"
        
        for result in results:
            context += f"[Источник {result['number']}] {result['title']}\n"
            context += f"URL: {result['link']}\n"
            
            if result.get('body'):
                context += f"СОДЕРЖИМОЕ:\n{result['body']}\n"
            
            context += "-" * 80 + "\n\n"
        
        context += "=== КОНЕЦ РЕЗУЛЬТАТОВ ===\n"
        context += "ВАЖНО: Используй ТЕКУЩУЮ ДАТУ из контекста для формирования актуального ответа.\n"
        
        logger.info(f"✅ Context: {len(context)} chars")
        return context

    def __del__(self):
        """Cleanup."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)