"""
DuckDuckGo search implementation using Playwright
"""
from typing import List, Dict, Optional
import asyncio
from playwright.async_api import async_playwright, Browser, Page
import json

class DuckDuckGoSearch:
    """DuckDuckGo search using Playwright for web scraping"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
        
    async def start(self):
        """Start the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo and return results
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of result dictionaries with 'title', 'url', 'snippet'
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        
        try:
            # Navigate to DuckDuckGo
            await page.goto(f"https://duckduckgo.com/?q={query}")
            
            # Wait for results to load
            await page.wait_for_selector('[data-result="organic"]', timeout=10000)
            
            # Extract results
            results = []
            result_elements = await page.query_selector_all('[data-result="organic"]')
            
            for element in result_elements[:max_results]:
                try:
                    # Extract title
                    title_elem = await element.query_selector('h2')
                    title = await title_elem.inner_text() if title_elem else "No title"
                    
                    # Extract URL
                    link_elem = await element.query_selector('a[href]')
                    url = await link_elem.get_attribute('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = await element.query_selector('[data-result="snippet"]')
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""
                    
                    results.append({
                        'title': title.strip(),
                        'url': url.strip(),
                        'snippet': snippet.strip()
                    })
                except Exception as e:
                    continue
                    
            return results
            
        finally:
            await page.close()
    
    def search_sync(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Synchronous wrapper for search
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        return asyncio.run(self.search(query, max_results))


async def search_duckduckgo(query: str, max_results: int = 5) -> str:
    """
    Search DuckDuckGo and return formatted results
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        Formatted JSON string with search results
    """
    async with DuckDuckGoSearch() as searcher:
        results = await searcher.search(query, max_results)
        
        return json.dumps({
            'query': query,
            'results_count': len(results),
            'results': results
        }, indent=2)


def search_duckduckgo_sync(query: str, max_results: int = 5) -> str:
    """
    Synchronous version of DuckDuckGo search
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        Formatted JSON string with search results
    """
    return asyncio.run(search_duckduckgo(query, max_results))
