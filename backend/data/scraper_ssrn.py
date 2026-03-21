"""
Octant AI module
writing this part was tricky ngl, just gluing things together atm
"""

import asyncio
import logging
from typing import List

from backend.data.literature_sources import PaperObject

logger = logging.getLogger(__name__)

class SSRNScraper:
    """Mocked SSRN scraper to remove Playwright dependency."""

    def __init__(self, gemini_client=None):
        self.gemini = gemini_client
    
    async def scrape(self, query: str, limit: int = 2) -> List[PaperObject]:
        """Navigate SSRN and extract paper details.
        
        Args:
            query: The search query string.
            limit: Number of papers to extract.
            
        Returns:
            List of PaperObject instances.
        """
        logger.info("SSRN Scraper (Mock) starting for query: %s", query)
        papers = []
        
        await asyncio.sleep(1) # simulate network delay
        
        for i in range(min(limit, 2)):
            papers.append(PaperObject(
                title=f"Sample SSRN Paper {i+1} on {query[:15]}...",
                authors="John Doe, Jane Doe",
                year=2023,
                journal_or_repo="SSRN",
                abstract=f"An abstract investigating {query} using advanced quantitative techniques.",
                url="https://ssrn.com/abstract=1234567"
            ))
            
        return papers
