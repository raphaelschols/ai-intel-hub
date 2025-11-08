"""
Research Collector - Gathers AI research papers from academic sources
"""

import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
import logging
import json
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class ResearchCollector:
    def __init__(self, research_sources: Dict[str, Any] = None):
        self.logger = logging.getLogger("research_collector")
        self.last_semantic_scholar_call = 0  # Track last API call time
    
    def gather_research_data(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI papers from arXiv and Semantic Scholar"""
        self.logger.info("Starting research paper collection")
        
        papers = []
        
        # Collect from arXiv (always reliable)
        arxiv_papers = self.collect_from_arxiv(max_results)
        papers.extend(arxiv_papers)
        
        # Collect from Semantic Scholar (with rate limiting)
        try:
            scholar_papers = self.collect_from_semantic_scholar(max_results // 2)  # Request fewer to avoid limits
            papers.extend(scholar_papers)
        except Exception as e:
            self.logger.warning(f"Semantic Scholar collection failed, continuing with arXiv only: {e}")
        
        self.logger.info(f"Collected {len(papers)} total papers")
        return papers
    
    def collect_from_arxiv(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI papers from arXiv"""
        self.logger.info("Fetching from arXiv...")
        
        url = f"http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        try:
            papers = []
            
            if HAS_REQUESTS:
                try:
                    response = requests.get(url, timeout=30)
                    xml_content = response.text
                except Exception:
                    # Fallback to urllib
                    with urllib.request.urlopen(url) as response:
                        xml_content = response.read().decode('utf-8')
            else:
                with urllib.request.urlopen(url) as response:
                    xml_content = response.read().decode('utf-8')
            
            # Parse XML with proper namespace handling
            root = ET.fromstring(xml_content)
            
            # Define namespace map for arXiv XML
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # Find all entry elements
            entries = root.findall('atom:entry', namespaces)
            
            for entry in entries:
                try:
                    # Extract title
                    title_elem = entry.find('atom:title', namespaces)
                    title = title_elem.text.strip() if title_elem is not None else "No title"
                    
                    # Extract summary
                    summary_elem = entry.find('atom:summary', namespaces)
                    summary = summary_elem.text.strip() if summary_elem is not None else "No summary"
                    
                    # Extract arXiv ID and create URL
                    id_elem = entry.find('atom:id', namespaces)
                    if id_elem is not None:
                        arxiv_id = id_elem.text.split('/')[-1]  # Extract ID from URL
                        url = f"https://arxiv.org/abs/{arxiv_id}"
                    else:
                        url = "No URL available"
                    
                    # Extract published date
                    published_elem = entry.find('atom:published', namespaces)
                    published = published_elem.text if published_elem is not None else ""
                    
                    # Extract authors
                    authors = []
                    author_elements = entry.findall('atom:author', namespaces)
                    for author in author_elements:
                        name_elem = author.find('atom:name', namespaces)
                        if name_elem is not None:
                            authors.append(name_elem.text)
                    
                    paper = {
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'source': 'arXiv',
                        'published_date': published,
                        'authors': authors,
                        'category': 'Research Paper'
                    }
                    
                    papers.append(paper)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing arXiv entry: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(papers)} papers from arXiv")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error fetching from arXiv: {e}")
            return []
    
    def collect_from_semantic_scholar(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get recent AI papers from Semantic Scholar with rate limiting"""
        self.logger.info("Fetching from Semantic Scholar...")
        
        # Rate limiting: wait at least 1 second between calls
        current_time = time.time()
        if current_time - self.last_semantic_scholar_call < 1.0:
            time.sleep(1.0 - (current_time - self.last_semantic_scholar_call))
        
        # Update call time
        self.last_semantic_scholar_call = time.time()
        
        try:
            papers = []
            
            # Search for recent AI papers
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': 'artificial intelligence machine learning',
                'limit': max_results,
                'fields': 'title,abstract,url,venue,year,authors,citationCount,publicationDate'
            }
            
            if HAS_REQUESTS:
                try:
                    response = requests.get(search_url, params=params, timeout=30)
                    if response.status_code == 429:  # Rate limited
                        self.logger.warning("Semantic Scholar rate limited, skipping")
                        return []
                    
                    if response.status_code != 200:
                        self.logger.warning(f"Semantic Scholar returned status {response.status_code}")
                        return []
                    
                    data = response.json()
                except Exception as e:
                    self.logger.warning(f"Requests failed for Semantic Scholar: {e}")
                    # Fallback to urllib
                    query_string = urllib.parse.urlencode(params)
                    url_with_params = f"{search_url}?{query_string}"
                    
                    with urllib.request.urlopen(url_with_params) as response:
                        if response.status == 429:
                            self.logger.warning("Semantic Scholar rate limited, skipping")
                            return []
                        data = json.loads(response.read().decode('utf-8'))
            else:
                query_string = urllib.parse.urlencode(params)
                url_with_params = f"{search_url}?{query_string}"
                
                with urllib.request.urlopen(url_with_params) as response:
                    if response.status == 429:
                        self.logger.warning("Semantic Scholar rate limited, skipping")
                        return []
                    data = json.loads(response.read().decode('utf-8'))
            
            # Process results
            if 'data' in data:
                for item in data['data']:
                    try:
                        # Extract authors
                        authors = []
                        if 'authors' in item and item['authors']:
                            authors = [author.get('name', 'Unknown') for author in item['authors']]
                        
                        paper = {
                            'title': item.get('title', 'No title'),
                            'summary': item.get('abstract', 'No abstract available'),
                            'url': item.get('url', 'No URL'),
                            'source': 'Semantic Scholar',
                            'published_date': item.get('publicationDate', ''),
                            'authors': authors,
                            'category': 'Research Paper',
                            'venue': item.get('venue', ''),
                            'citation_count': item.get('citationCount', 0),
                            'year': item.get('year', '')
                        }
                        
                        papers.append(paper)
                        
                    except Exception as e:
                        self.logger.warning(f"Error parsing Semantic Scholar entry: {e}")
                        continue
            
            self.logger.info(f"Retrieved {len(papers)} papers from Semantic Scholar")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error fetching from Semantic Scholar: {e}")
            return []


# Test function
def test_research_collector():
    """Test the research collector"""
    collector = ResearchCollector()
    papers = collector.gather_research_data(max_results=5)
    
    print(f"Collected {len(papers)} papers:")
    for paper in papers[:3]:  # Show first 3
        print(f"- {paper['title'][:80]}... ({paper['source']})")

if __name__ == "__main__":
    test_research_collector()