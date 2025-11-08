import schedule
import time
import json
import os
from datetime import datetime
from assistants.telegram_bot import TelegramBot
from pipeline.orchestrator import ContentPipeline

def run_weekly_summary():
    """Run the content pipeline and send weekly summary via Telegram"""
    try:
        # Initialize pipeline and bot
        pipeline = ContentPipeline()
        bot = TelegramBot()
        
        # Generate fresh content
        print("Running weekly content pipeline...")
        results = pipeline.run_complete_pipeline()
        
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
        
        # Send summary
        print("Sending weekly summary...")
        bot.send_daily_summary(articles=articles)
        
        print("Weekly summary sent successfully!")
        
    except Exception as e:
        print(f"Error in weekly summary: {e}")

# Schedule weekly summary every Monday at 9:00 AM

#schedule.every().saturday.at("11:28").do(run_weekly_summary)
schedule.every(15).minutes.do(run_weekly_summary)
#schedule.every().day.at("09:00").do(run_weekly_summary)

if __name__ == "__main__":
    print("Scheduler started. Weekly summaries will be sent every Monday at 9:00 AM")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute