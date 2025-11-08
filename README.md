# AI Tracker - Multi-Agent AI Development Monitoring System

A sophisticated multi-agent system that automatically tracks, analyzes, and ranks AI developments from multiple sources, delivering insights through a beautiful dashboard and WhatsApp notifications.

## 🚀 Features

### Multi-Agent Architecture
- **RSS Agent**: Collects AI news from feeds (arXiv, MIT Tech Review, company blogs)
- **Research Agent**: Scrapes academic papers from arXiv and Semantic Scholar
- **Ranking Agent**: Intelligently ranks content by importance and relevance
- **WhatsApp Agent**: Sends notifications and digests via WhatsApp
- **Orchestrator**: Coordinates all agents and manages the workflow

### Intelligent Dashboard
- Dark-themed, responsive UI optimized for content consumption
- Real-time system status and collection progress
- Category filtering and search capabilities
- Importance scoring and ranking display
- Automatic post and project idea generation

### Smart Notifications
- Daily digest summaries via WhatsApp
- Breaking news alerts for high-importance topics
- Weekly analytics summaries
- Custom alerts for trending topics

## 📁 Project Structure

```
focus-feed/
├── agents/                     # Multi-agent system
│   ├── rss_agent.py           # RSS feed collection
│   ├── research_agent.py      # Academic paper scraping
│   ├── ranking_agent.py       # Importance ranking
│   └── whatsapp_notification_agent.py  # WhatsApp notifications
├── config/
│   └── config.json            # System configuration
├── data/                      # Database and data storage
├── logs/                      # System logs
├── templates/
│   └── index.html             # Dashboard template
├── utils/
│   ├── database.py            # Database management
│   └── logger.py              # Logging utilities
├── app.py                     # Flask web application
├── orchestrator.py            # Main coordination system
├── whatsapp_agent.py          # Legacy WhatsApp functionality
└── requirements.txt           # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Twilio account (for WhatsApp notifications)

### Setup Instructions

1. **Clone and install dependencies**:
```bash
git clone <repository-url>
cd focus-feed
pip install -r requirements.txt
```

2. **Configure Twilio credentials**:
   - Edit `config/config.json`
   - Replace placeholders in the `twilio` section:
     - `account_sid`: Your Twilio Account SID
     - `auth_token`: Your Twilio Auth Token
     - `from_whatsapp_number`: Your Twilio WhatsApp number
     - `recipients`: List of WhatsApp numbers to receive notifications

3. **Optional: Configure Semantic Scholar API**:
   - Get API key from [Semantic Scholar](https://www.semanticscholar.org/product/api)
   - Add to `config.json` under `research_sources.semantic_scholar.api_key`

## 🚀 Usage

### Start the Dashboard
```bash
python app.py
```
Visit http://localhost:5000 to view the dashboard.

### Run Manual Collection
```bash
python orchestrator.py
```

### Run with Scheduling
```python
from orchestrator import AITrackerOrchestrator

orchestrator = AITrackerOrchestrator()
orchestrator.start_scheduler()  # Runs automatically every 6 hours
```

### Test WhatsApp Integration
```bash
python agents/whatsapp_notification_agent.py
```

## 📊 Dashboard Features

### Main Interface
- **System Status**: Real-time monitoring of agent status
- **Collection Controls**: Manual trigger for data collection
- **Category Filters**: Filter by Research, News, Blogs, etc.
- **Analytics View**: Source distribution and keyword trends

### Topic Cards
- **Importance Ranking**: Visual ranking badges (#1, #2, etc.)
- **Source Indicators**: Color-coded source banners
- **Metadata**: Publication dates, citation counts
- **AI Keywords**: Extracted relevant keywords
- **Generated Ideas**: Automated post and project suggestions

## 🔧 Configuration

### RSS Sources (`config.json`)
Add or modify RSS feeds in the `rss_sources` array:
```json
{
  "name": "Source Name",
  "url": "https://example.com/feed.xml",
  "category": "Research Paper",
  "color": "#4CAF50",
  "enabled": true
}
```

### Ranking Criteria
Adjust ranking weights in `ranking_criteria`:
- `recency_weight`: How recent the content is
- `citation_weight`: Citation count importance
- `keyword_weight`: AI keyword relevance
- `source_weight`: Source credibility
- `novelty_weight`: Content novelty
- `engagement_weight`: Estimated engagement potential

### WhatsApp Notifications
Configure notification types in `twilio.notifications`:
- `daily_digest`: Enable/disable daily summaries
- `breaking_news_threshold`: Importance score threshold for alerts
- `weekly_summary`: Enable/disable weekly analytics
- `high_activity_alerts`: Alerts for trending topics

## 🤖 Agent Details

### RSS Agent
- Monitors 10+ AI-focused RSS feeds
- Filters for AI-related content
- Extracts keywords and metadata
- Handles rate limiting and errors gracefully

### Research Agent
- arXiv API integration for latest papers
- Semantic Scholar API for citation data
- Quality filtering based on citations and recency
- Duplicate detection and removal

### Ranking Agent
- Multi-factor importance scoring
- Keyword analysis and trend detection
- Source credibility weighting
- Bonus multipliers for breakthrough content

### WhatsApp Agent
- Twilio API integration
- Multiple notification types
- Error handling and retry logic
- Message formatting and templates

## 📈 Analytics

The system provides comprehensive analytics:
- **Daily Collection Metrics**: Items collected and processed
- **Source Distribution**: Content breakdown by source
- **Keyword Trends**: Most mentioned AI topics
- **Importance Scoring**: Average content quality metrics

## 🔍 API Endpoints

- `GET /api/topics`: Retrieve topics with pagination
- `GET /api/run_collection`: Trigger manual collection
- `GET /api/analytics`: Get system analytics
- `GET /api/system_status`: Check system health

## 🔧 Maintenance

### Database Cleanup
```python
from utils.database import DatabaseManager
db = DatabaseManager()
db.cleanup_old_data(days_to_keep=90)
```

### Log Management
Logs automatically rotate at 10MB with 5 backup files retained.

### Data Backup
The SQLite database is stored in `data/ai_tracker.db` - backup regularly.

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

2. **Database Errors**: Check that the `data/` directory exists and is writable

3. **WhatsApp Failures**: Verify Twilio credentials and WhatsApp number format

4. **RSS Feed Timeouts**: Check internet connectivity and RSS source availability

### Debug Mode
Enable debug logging by setting `logging.level` to `DEBUG` in `config.json`.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- arXiv for providing free access to research papers
- Semantic Scholar for citation data
- Twilio for WhatsApp API integration
- Various AI news sources for RSS feeds