"""
RSS Collector - Gathers AI news and developments from RSS feeds
"""

import requests
import feedparser
import logging
from datetime import datetime
from typing import List, Dict, Any
import re

class RSSCollector:
    def __init__(self, rss_sources: List[Dict[str, str]] = None):
        self.rss_sources = rss_sources or self.get_default_sources()
        self.logger = logging.getLogger("rss_collector")
    
    def get_default_sources(self) -> List[Dict[str, str]]:
        """Default RSS sources for AI news"""
        return [
            {
                "name": "MIT Technology Review AI",
                "url": "https://www.technologyreview.com/feed/",
                "category": "News"
            },
            {
                "name": "Anthropic Blog",
                "url": "https://www.anthropic.com/feed.xml",
                "category": "AI Research"
            },
            {
                "name": "OpenAI Blog",
                "url": "https://openai.com/blog/rss.xml",
                "category": "Company Blog"
            },
            {
                "name": "Google AI Blog",
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "category": "Company Blog"
            }
        ]
    
    def gather_rss_data(self, max_sources: int = None) -> List[Dict[str, Any]]:
        """Collect data from all RSS sources"""
        self.logger.info("Starting RSS data collection")
        
        all_items = []
        sources_to_process = self.rss_sources[:max_sources] if max_sources else self.rss_sources
        
        for source in sources_to_process:
            items = self.fetch_rss_feed(source)
            all_items.extend(items)
        
        self.logger.info(f"Collected {len(all_items)} total items from RSS feeds")
        return all_items
    
    def fetch_rss_feed(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed"""
        self.logger.info(f"Fetching from {source['name']}...")
        
        try:
            response = requests.get(source["url"], timeout=30)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch {source['name']}: HTTP {response.status_code}")
                return []
            
            return self.parse_rss_content(response.text, source)
            
        except Exception as e:
            self.logger.error(f"Error fetching {source['name']}: {e}")
            return []
    
    def parse_rss_content(self, content: str, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse RSS content and extract relevant information"""
        try:
            feed = feedparser.parse(content)
            items = []
            
            for entry in feed.entries[:5]:  # Limit to 5 most recent
                try:
                    # Extract content
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = self.clean_html(entry.summary)
                    elif hasattr(entry, 'description'):
                        summary = self.clean_html(entry.description)
                    
                    item = {
                        "title": entry.title if hasattr(entry, 'title') else "No Title",
                        "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                        "url": entry.link if hasattr(entry, 'link') else "",
                        "source": source["name"],
                        "category": source["category"],
                        "published_date": datetime.now().isoformat(),
                        "collector": "rss",
                        "keywords": self.extract_simple_keywords(entry.title + " " + summary)
                    }
                    
                    # Filter for AI-related content
                    if self.is_ai_related(item):
                        items.append(item)
                
                except Exception as e:
                    self.logger.warning(f"Error parsing entry from {source['name']}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(items)} items from {source['name']}")
            return items
            
        except Exception as e:
            self.logger.error(f"Error parsing RSS from {source['name']}: {e}")
            return []
    
    def clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def extract_simple_keywords(self, text: str) -> List[str]:
        """Extract simple keywords from text"""
        if not text:
            return []
        
        # AI-related keywords to look for
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'AI', 'ML', 'algorithm', 'automation',
            'computer vision', 'natural language', 'robotics', 'chatbot',
            'LLM', 'transformer', 'GPT', 'BERT', 'claude', 'openai'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in ai_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Limit to 5 keywords
    
    def is_ai_related(self, item: Dict[str, Any]) -> bool:
        """Check if an item is AI-related"""
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
        ai_terms = [
            'ai', 'artificial intelligence', 'machine learning', 'ml',
            'deep learning', 'neural network', 'algorithm', 'automation',
            'computer vision', 'natural language', 'nlp', 'robotics',
            'chatbot', 'llm', 'gpt', 'transformer', 'openai', 'claude'
        ]
        
        return any(term in text for term in ai_terms)