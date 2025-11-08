"""
Idea Generator - AI-powered content idea creation from research sources
"""

import logging
import os
from typing import List, Dict, Any
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

class IdeaGenerator:
    def __init__(self, openai_api_key: str = OPENAI_API_KEY):
        self.logger = logging.getLogger("idea_generator")
        
        self.client = None
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.logger.warning("No OpenAI API key provided")
    
    def create_content_ideas(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate post and article ideas for each source article"""
        
        if not self.client:
            self.logger.warning("OpenAI client not available, cannot generate ideas")
            return articles
        
        enhanced_articles = []
        
        for article in articles:
            try:
                # Extract title and summary
                title = article.get('title', '')
                summary = article.get('summary', article.get('description', ''))
                
                # Generate ideas using GPT-4 mini
                post_idea, article_idea = self._generate_ideas_for_article(title, summary)
                
                # Create flattened result by copying original article and adding ideas
                enhanced_article = article.copy()  # Copy all original data
                enhanced_article.update({
                    'post_idea': post_idea,
                    'article_idea': article_idea
                })
                
                enhanced_articles.append(enhanced_article)
                
            except Exception as e:
                self.logger.error(f"Error generating ideas for article '{title}': {e}")
                # Add fallback entry with original data
                fallback_article = article.copy()
                fallback_article.update({
                    'post_idea': "Error generating post idea",
                    'article_idea': "Error generating article idea"
                })
                enhanced_articles.append(fallback_article)
        
        return enhanced_articles
    
    def _generate_ideas_for_article(self, title: str, summary: str) -> tuple:
        """Generate post and article ideas for a single article using GPT-4 mini"""
        
        prompt = f"""
Based on this research article, generate content ideas:

Title: {title}
Summary: {summary}

Please provide:
1. ONE social media post idea (5 sentences max) - engaging, shareable content that highlights the key insight
2. ONE article idea (5 sentences max) - a deeper dive or practical application of this research

Format your response exactly like this:
POST IDEA: [your post idea here]
ARTICLE IDEA: [your article idea here]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative content strategist who generates engaging social media posts and article ideas based on AI/tech research. Keep responses concise and actionable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Parse the response
            post_idea = ""
            article_idea = ""
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith('POST IDEA:'):
                    post_idea = line.replace('POST IDEA:', '').strip()
                elif line.startswith('ARTICLE IDEA:'):
                    article_idea = line.replace('ARTICLE IDEA:', '').strip()
            
            # Fallback parsing if format isn't exact
            if not post_idea or not article_idea:
                parts = content.split('ARTICLE IDEA:')
                if len(parts) == 2:
                    post_part = parts[0].replace('POST IDEA:', '').strip()
                    article_part = parts[1].strip()
                    post_idea = post_part if post_part else "Generated post idea"
                    article_idea = article_part if article_part else "Generated article idea"
                else:
                    post_idea = content[:150] + "..." if len(content) > 150 else content
                    article_idea = "Related article opportunity"
            
            return post_idea, article_idea
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            return "Error generating post idea", "Error generating article idea"
    
    def get_ideas_summary(self, articles_with_ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of generated ideas"""
        return {
            'total_articles': len(articles_with_ideas),
            'post_ideas': [article.get('post_idea', '') for article in articles_with_ideas],
            'article_ideas': [article.get('article_idea', '') for article in articles_with_ideas],
            'articles_with_ideas': len([article for article in articles_with_ideas if article.get('post_idea') and article.get('article_idea')])
        }


# Test function
def test_idea_generator():
    """Test the idea generator with sample data"""
    test_articles = [
        {
            'title': 'Breakthrough in Neural Network Efficiency',
            'summary': 'Researchers develop new pruning technique that reduces model size by 90% while maintaining accuracy',
            'url': 'https://example.com/1'
        },
        {
            'title': 'AI-Powered Drug Discovery Advances',
            'summary': 'Machine learning algorithm identifies potential COVID treatments in record time',
            'url': 'https://example.com/2'
        }
    ]
    
    generator = IdeaGenerator()
    enhanced_articles = generator.create_content_ideas(test_articles)
    
    for article in enhanced_articles:
        print(f"Title: {article.get('title', 'No title')}")
        print(f"Post Idea: {article.get('post_idea', 'No post idea')}")
        print(f"Article Idea: {article.get('article_idea', 'No article idea')}")
        print("-" * 50)

if __name__ == "__main__":
    test_idea_generator()