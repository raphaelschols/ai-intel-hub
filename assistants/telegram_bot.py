"""
Simple Telegram Bot - Sends AI content summaries with weekly scheduling
"""
import os
import requests
from datetime import datetime

content_engine_https = os.getenv("CONTENT_ENGINE_HTTPS")

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    def set_chat_id(self):
        """Get your chat ID - run this first!"""
        if not self.bot_token:
            print("Missing TELEGRAM_BOT_TOKEN")
            return None
        
        if not self.chat_id:
            print("Fetching chat ID...")
            
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                chat_id = data['result'][-1]['message']['chat']['id']
                print(f"Your Chat ID is: {chat_id}")
                print(f"Setting TELEGRAM_CHAT_ID={chat_id}")
                self.chat_id = chat_id
                return self.chat_id
            else:
                print("No messages found. Send a message to your bot first.")
                return None
        
    def send_message(self, text: str) -> bool:
        """Send message to Telegram"""
        if not self.bot_token:
            print("Missing TELEGRAM_BOT_TOKEN")
            return False
        if not self.chat_id:
            self.set_chat_id()
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {'chat_id': self.chat_id, 'text': text}
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("Message sent!")
                return True
            else:
                print(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def send_daily_summary(self, articles: list[dict]) -> None:
        """Send daily summary of top articles"""

        if len(articles) == 0:

            self.send_message("🤖 Daily AI Summary\n\nNo articles found today.")

            return None
            
            # Build message
        message = f"🤖 Daily AI Summary - {datetime.now().strftime('%B %d')}\n\n"
        message += f"Click here to read more articles: {content_engine_https}\n\nTop Articles:\n\n"

        for i, article in enumerate(articles, start=1):
            title = article["title"]
            message += f"{i}. {title}\n"
            message += f"   {article['url']}\n\n"

        self.send_message(message)
        
"""Test sending a message"""
def test_send_message():

    test_article_list = [
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

    bot = TelegramBot()
    bot.send_daily_summary(articles=test_article_list)

