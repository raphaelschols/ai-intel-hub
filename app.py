from flask import Flask, render_template, jsonify
from pipeline.orchestrator import ContentPipeline
import platform
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_feed_data():
    """Load saved feed data or generate fresh if file doesn't exist"""
    data_file = "data/latest_feed.json"
    
    # Try to load saved data first
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded cached data from {data['last_updated']}")
                return data.get('content_ideas', [])
        except Exception as e:
            print(f"Error loading saved data: {e}")
    
    # Fallback: generate fresh data if no saved file
    print("No cached data found, generating fresh content...")
    pipeline = ContentPipeline()
    results = pipeline.run_complete_pipeline(top_n=10)
    return results.get('content_ideas', []) if results else []

@app.route('/')
def simple_feed():
    """Card-based scrollable feed"""
    try:
        # Load articles from saved data
        articles = load_feed_data()
        
        # Ensure articles is a list
        if not isinstance(articles, list):
            articles = []
        
        # Create HTML cards
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Content Intelligence Feed</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f7fa;
                    line-height: 1.6;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    position: relative;
                }}
                
                .dark-mode-toggle {{
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: #f3f4f6;
                    border: 2px solid #e5e7eb;
                    border-radius: 25px;
                    padding: 8px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                
                .dark-mode-toggle:hover {{
                    background: #e5e7eb;
                    transform: scale(1.05);
                }}
                
                .theme-icon {{
                    font-size: 16px;
                }}
                
                .stats {{
                    display: flex;
                    justify-content: center;
                    gap: 30px;
                    margin-top: 15px;
                }}
                
                .stat {{
                    text-align: center;
                }}
                
                .stat-number {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                }}
                
                .stat-label {{
                    font-size: 12px;
                    color: #6b7280;
                    text-transform: uppercase;
                }}
                
                .feed-container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .article-card {{
                    background: white;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    padding: 25px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease;
                }}
                
                .article-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                }}
                
                .card-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 15px;
                }}
                
                .article-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #1f2937;
                    margin: 0;
                    flex: 1;
                    margin-right: 15px;
                }}
                
                .category-badge {{
                    background: #ddd6fe;
                    color: #7c3aed;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 500;
                    white-space: nowrap;
                }}
                
                .keywords {{
                    margin-bottom: 15px;
                }}
                
                .keyword-tag {{
                    background: #f3f4f6;
                    color: #6b7280;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    margin-right: 5px;
                    display: inline-block;
                }}
                
                .summary {{
                    color: #4b5563;
                    margin-bottom: 20px;
                    font-size: 14px;
                }}
                
                .ideas-section {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                
                .idea-box {{
                    background: #f8fafc;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                }}
                
                .idea-title {{
                    font-weight: 600;
                    color: #1f2937;
                    margin-bottom: 8px;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .idea-content {{
                    font-size: 14px;
                    color: #4b5563;
                }}
                
                .article-footer {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding-top: 15px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 12px;
                    color: #6b7280;
                }}
                
                .footer-left {{
                    display: flex;
                    gap: 15px;
                }}
                
                .source-link {{
                    color: #3b82f6;
                    text-decoration: none;
                }}
                
                .source-link:hover {{
                    text-decoration: underline;
                }}
                
                .relevance-score {{
                    background: #dcfce7;
                    color: #16a34a;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-weight: 500;
                }}
                
                @media (max-width: 768px) {{
                    .ideas-section {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .article-footer {{
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 10px;
                    }}
                    
                    .dark-mode-toggle {{
                        position: static;
                        margin: 10px auto 0;
                    }}
                }}
                
                /* Dark Mode Styles */
                .dark-mode {{
                    background-color: #0f172a !important;
                    color: #e2e8f0 !important;
                }}
                
                .dark-mode .header {{
                    background: #1e293b !important;
                    color: #e2e8f0 !important;
                }}
                
                .dark-mode .article-card {{
                    background: #1e293b !important;
                    color: #e2e8f0 !important;
                }}
                
                .dark-mode .article-title {{
                    color: #f1f5f9 !important;
                }}
                
                .dark-mode .summary {{
                    color: #cbd5e1 !important;
                }}
                
                .dark-mode .idea-box {{
                    background: #0f172a !important;
                    color: #e2e8f0 !important;
                }}
                
                .dark-mode .idea-title {{
                    color: #f1f5f9 !important;
                }}
                
                .dark-mode .idea-content {{
                    color: #cbd5e1 !important;
                }}
                
                .dark-mode .article-footer {{
                    border-top: 1px solid #334155 !important;
                    color: #94a3b8 !important;
                }}
                
                .dark-mode .source-link {{
                    color: #60a5fa !important;
                }}
                
                .dark-mode .keyword-tag {{
                    background: #334155 !important;
                    color: #94a3b8 !important;
                }}
                
                .dark-mode .dark-mode-toggle {{
                    background: #334155 !important;
                    border-color: #475569 !important;
                    color: #e2e8f0 !important;
                }}
                
                .dark-mode .dark-mode-toggle:hover {{
                    background: #475569 !important;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <button class="dark-mode-toggle" onclick="toggleDarkMode()">
                    <span class="theme-icon">🌙</span>
                    <span class="theme-text">Dark</span>
                </button>
                <h1>🤖 AI Content Intelligence Feed</h1>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{len(articles)}</div>
                        <div class="stat-label">Articles</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">10</div>
                        <div class="stat-label">Top Ranked</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(articles)}</div>
                        <div class="stat-label">Ideas Generated</div>
                    </div>
                </div>
            </div>
            
            <div class="feed-container">
        """
        
        # Generate article cards
        for i, article in enumerate(articles, 1):
            # Safety check for None articles
            if not article or not isinstance(article, dict):
                continue
                
            title = article.get('title', 'No Title')
            summary = article.get('summary', 'No summary available')
            category = article.get('category', 'Unknown')
            source = article.get('source', 'Unknown')
            url = article.get('url', '#')
            published_date = article.get('published_date', 'Unknown date')
            post_idea = article.get('post_idea', 'No post idea generated')
            article_idea = article.get('article_idea', 'No article idea generated')
            relevance_score = article.get('relevance_score', 0)
            keywords = article.get('keywords', [])
            
            # Ensure safe types
            if not isinstance(title, str):
                title = str(title) if title is not None else 'No Title'
            if not isinstance(summary, str):
                summary = str(summary) if summary is not None else 'No summary available'
            if not isinstance(keywords, list):
                keywords = []
            
            # Format relevance score (scale 0-10)
            score_display = f"{relevance_score * 10:.1f}" if isinstance(relevance_score, (int, float)) else str(relevance_score)

            # Show more summary text (up to 800 chars)
            summary_display = summary[:800] + ('...' if len(summary) > 800 else '')

            # Format keywords
            keywords_html = ""
            if keywords and isinstance(keywords, list):
                keywords_html = "".join([f'<span class="keyword-tag">{keyword}</span>' for keyword in keywords[:5]])
            
            html_content += f"""
                <div class="article-card">
                    <div class="card-header">
                        <h2 class="article-title">{title}</h2>
                        <span class="category-badge">{category}</span>
                    </div>
                    <div class="keywords">
                        {keywords_html}
                    </div>
                    <div class="summary">
                        {summary_display}
                    </div>
                    <div class="ideas-section">
                        <div class="idea-box">
                            <div class="idea-title">📱 Post Idea</div>
                            <div class="idea-content">{post_idea}</div>
                        </div>
                        <div class="idea-box">
                            <div class="idea-title">📄 Article Idea</div>
                            <div class="idea-content">{article_idea}</div>
                        </div>
                    </div>
                    <div class="article-footer">
                        <div class="footer-left">
                            <a href="{url}" class="source-link" target="_blank">🔗 {source}</a>
                            <span>📅 {published_date}</span>
                        </div>
                        <span class="relevance-score">⭐ {score_display}</span>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
            
            <script>
                function toggleDarkMode() {
                    const body = document.body;
                    const toggle = document.querySelector('.dark-mode-toggle');
                    const icon = toggle.querySelector('.theme-icon');
                    const text = toggle.querySelector('.theme-text');
                    
                    body.classList.toggle('dark-mode');
                    
                    if (body.classList.contains('dark-mode')) {
                        icon.textContent = '☀️';
                        text.textContent = 'Light';
                        localStorage.setItem('darkMode', 'enabled');
                    } else {
                        icon.textContent = '🌙';
                        text.textContent = 'Dark';
                        localStorage.setItem('darkMode', 'disabled');
                    }
                }
                
                // Check for saved dark mode preference or default to light mode
                const savedTheme = localStorage.getItem('darkMode');
                if (savedTheme === 'enabled') {
                    document.body.classList.add('dark-mode');
                    document.querySelector('.theme-icon').textContent = '☀️';
                    document.querySelector('.theme-text').textContent = 'Light';
                }
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"""
        <html>
        <body style="font-family: monospace; padding: 20px; background: #f5f5f5;">
            <h1>Error in AI Content Feed</h1>
            <h2>Error: {str(e)}</h2>
            <h3>Detailed traceback:</h3>
            <pre style="background: white; padding: 20px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>
            <p><a href="/">Try refreshing the page</a></p>
        </body>
        </html>
        """

@app.route('/api/data')
def get_data():
    """API endpoint to get processed data"""
    try:
        # Load articles from saved data
        articles = load_feed_data()
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_collected': len(articles),
            'top_ranked': len(articles),
            'ideas_generated': len(articles),
            'content_ideas': articles,
            'ranked_articles': articles
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'data': []
        }), 500

if __name__ == '__main__':
    print("Starting AI Focus Feed Dashboard...")
    
    # Disable reloader on Windows to avoid signal issues
    is_windows = platform.system() == 'Windows'
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=not is_windows)