"""
Content Intelligence Pipeline
Main orchestrator that coordinates all collectors and intelligence components
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Updated imports for new structure
from collectors.research_collector import ResearchCollector
from collectors.rss_collector import RSSCollector
from assistants.content_ranker import ContentRanker
from assistants.idea_generator import IdeaGenerator
from assistants.telegram_bot import TelegramBot

class ContentPipeline:
    def __init__(self):
        self.research_collector = ResearchCollector()
        self.rss_collector = RSSCollector()
        self.content_ranker = ContentRanker()
        self.idea_generator = IdeaGenerator()
        self.logger = logging.getLogger("content_pipeline")
    
    def gather_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data from all sources"""
        self.logger.info("Starting data collection from all sources")
        
        try:
            # Collect from research sources
            research_data = self.research_collector.gather_research_data(max_results=10)
            
            # Collect from RSS sources  
            rss_data = self.rss_collector.gather_rss_data()
            
            data_collected = {
                "research": research_data,
                "rss": rss_data
            }
            
            total_items = len(research_data) + len(rss_data)
            self.logger.info(f"Collected {total_items} total items")
            
            return data_collected
            
        except Exception as e:
            self.logger.error(f"Error during data collection: {e}")
            return {"research": [], "rss": []}
    
    def clean_and_structure_data(self, raw_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Clean and structure data for processing"""
        self.logger.info("Cleaning and structuring collected data")
        
        structured = []
        
        for source_type, items in raw_data.items():
            if isinstance(items, list) and items:
                for item in items:
                    structured_item = {
                        "title": item.get("title", ""),
                        "summary": item.get("summary", ""),
                        "source": item.get("source", ""),
                        "url": item.get("url", ""),
                        "published_date": item.get("published_date", ""),
                        "category": item.get("category", ""),
                        "keywords": item.get("keywords", []),
                        "source_type": source_type,
                        "original_data": item  # Keep reference to original
                    }
                    structured.append(structured_item)
        
        self.logger.info(f"Structured {len(structured)} items")
        return structured
    
    def rank_content_by_relevance(self, articles: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Rank content using AI-powered relevance scoring"""
        self.logger.info(f"Ranking content and selecting top {top_n} items")
        
        try:
            ranked_articles = self.content_ranker.get_top_content(articles, top_x=top_n)
            
            self.logger.info(f"Successfully ranked and selected {len(ranked_articles)} top articles")
            return ranked_articles
            
        except Exception as e:
            self.logger.error(f"Error during content ranking: {e}")
            return articles[:top_n]  # Fallback to first N items
    
    def generate_creative_ideas(self, ranked_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate creative content ideas from ranked articles"""
        self.logger.info("Generating creative content ideas")
        
        try:
            ideas = self.idea_generator.create_content_ideas(ranked_articles)
            
            self.logger.info(f"Generated ideas for {len(ideas)} articles")
            return ideas
            
        except Exception as e:
            self.logger.error(f"Error during idea generation: {e}")
            # Fallback: add placeholder ideas
            for article in ranked_articles:
                article["post_idea"] = "Manual post idea needed"
                article["article_idea"] = "Manual article idea needed"
            return ranked_articles
    
    def run_complete_pipeline(self, top_n: int = 10) -> Dict[str, Any]:
        """Run the complete content intelligence pipeline"""
        self.logger.info("Starting complete content intelligence pipeline")
        
        try:
            # Step 1: Gather data from all sources
            raw_data = self.gather_all_data()
            
            # Step 2: Clean and structure the data
            structured_data = self.clean_and_structure_data(raw_data)
            
            # Step 3: Rank content by AI relevance
            ranked_content = self.rank_content_by_relevance(structured_data, top_n)
            
            # Step 4: Generate creative ideas
            final_ideas = self.generate_creative_ideas(ranked_content)
            
            # Step 5: Create summary
            pipeline_results = {
                "timestamp": datetime.now().isoformat(),
                "total_collected": len(structured_data),
                "top_ranked": len(ranked_content),
                "ideas_generated": len(final_ideas),
                "ranked_articles": ranked_content,
                "content_ideas": final_ideas,
                "sources_used": list(raw_data.keys())
            }
            
            self.logger.info("Pipeline completed successfully")
            return pipeline_results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
    
    def generate_content_and_notify(self):
        """Generate fresh content pipeline results and send notification via Telegram"""
        try:
            # Initialize telegram bot
            bot = TelegramBot()
            
            # Generate fresh content
            print("Running content pipeline...")
            results = self.run_complete_pipeline()
            
            # Save results to file for web app to use
            data_file = "data/latest_feed.json"
            os.makedirs("data", exist_ok=True)
            
            feed_data = {
                "last_updated": datetime.now().isoformat(),
                "content_ideas": results.get('content_ideas', [])
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(feed_data, f, indent=2, ensure_ascii=False)
            
            print(f"Results saved to {data_file}")

            # Read articles from saved data
            with open(data_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                articles = saved_data.get('content_ideas', [])
            
            # Send notification
            print("Sending content summary...")
            bot.send_daily_summary(articles=articles)
            
            print("Content generation and notification completed successfully!")
            
        except Exception as e:
            print(f"Error in content generation and notification: {e}")
            self.logger.error(f"Error in content generation and notification: {e}")
            raise
