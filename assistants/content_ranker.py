"""
Content Ranker - AI-powered content relevance scoring using embeddings
"""

import logging
from typing import List, Dict, Any
import os
import openai
import numpy as np

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

class ContentRanker:
    def __init__(self, openai_api_key: str = OPENAI_API_KEY):
        self.logger = logging.getLogger("content_ranker")
        
        # Standard AI relevance sentence to compare against
        self.reference_text = (
            "artificial intelligence research or developments that is both groundbreaking and practical, "
            "with clear real-world applications, valuable insights, or potential for projects "
            "that teach data science and machine learning skills."
        )
        
        self.client = None
        if openai_api_key:
            openai.api_key = openai_api_key
            self.client = openai
    
    def score_content_relevance(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score articles by embedding similarity to AI reference text"""
        
        if not self.client:
            self.logger.warning("OpenAI client not available, returning original order")
            for i, article in enumerate(articles):
                article["relevance_score"] = 0.5
                article["rank"] = i + 1
            return articles
        
        try:
            # Get reference embedding
            ref_embedding = self._get_embedding(self.reference_text)
            
            # Score each article
            for article in articles:
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                article_embedding = self._get_embedding(text)
                similarity = self._cosine_similarity(ref_embedding, article_embedding)
                article["relevance_score"] = similarity
            
            # Sort by score (highest first)
            ranked = sorted(articles, key=lambda x: x["relevance_score"], reverse=True)
            
            # Add rank positions
            for i, article in enumerate(ranked):
                article["rank"] = i + 1
                
            return ranked
            
        except Exception as e:
            self.logger.error(f"Content ranking failed: {e}")
            return articles
    
    def get_top_content(self, articles: List[Dict[str, Any]], top_x: int = 5) -> List[Dict[str, Any]]:
        """Get the top X ranked articles by AI relevance"""
        ranked_articles = self.score_content_relevance(articles)
        return ranked_articles[:top_x]
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        if not self.client:
            self.logger.warning("OpenAI client not available")
            return []
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error getting embedding: {e}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        if not a or not b:
            return 0.0
        
        a_np, b_np = np.array(a), np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))


# Test function
def test_content_ranker():
    """Test the content ranker"""
    test_articles = [
        {
            'title': 'AI breakthrough in machine learning',
            'summary': 'new neural network architecture for computer vision',
            'url': 'https://example.com/1'
        },
        {
            'title': 'cooking recipe tips',
            'summary': 'how to make the perfect pasta sauce',
            'url': 'https://example.com/2'
        }
    ]
    
    ranker = ContentRanker()
    ranked = ranker.score_content_relevance(test_articles)
    
    print("Ranked articles:")
    for article in ranked:
        score = article.get('relevance_score', 'N/A')
        print(f"- {article['title']} (score: {score})")

if __name__ == "__main__":
    test_content_ranker()