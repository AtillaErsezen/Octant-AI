"""
Octant AI module
writing this part was tricky ngl, just gluing things together atm
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RedditComment:
    author: str
    body: str
    upvotes: int
    tickers_mentioned: List[str] = field(default_factory=list)


@dataclass
class RedditPost:
    title: str
    url: str
    upvotes: int
    post_time: str
    tickers_mentioned: List[str] = field(default_factory=list)
    top_comments: List[RedditComment] = field(default_factory=list)


class RedditScraper:
    """Mocked Reddit scraper to remove Playwright dependency."""

    def __init__(self, target_subreddits: Optional[List[str]] = None):
        self.subreddits = target_subreddits or [
            "wallstreetbets", "stocks", "investing"
        ]

    async def scrape(self, ticker_list: Optional[List[str]] = None) -> List[RedditPost]:
        """Mocked Reddit scrape to remove Playwright dependency.
        
        Returns:
            An empty list or mocked subset of RedditPost objects.
        """
        logger.info("Starting mock Reddit scraper on %d subreddits", len(self.subreddits))
        all_posts: List[RedditPost] = []
        
        await asyncio.sleep(1) # simulate network delay
        
        return all_posts
