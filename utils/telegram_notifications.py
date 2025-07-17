#!/usr/bin/env python3
"""
Telegram notification service for webhooks
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TelegramNotificationService:
    """Send notifications via Telegram without loading main.py"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
    
    def send_message(self, chat_id: str, message: str) -> bool:
        """Send message directly to Telegram"""
        if not self.bot_token:
            logger.error("Cannot send message - bot token not configured")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_id}")
                return True
            else:
                logger.error(f"❌ Failed to send message to {chat_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message to {chat_id}: {e}")
            return False

# Global instance for webhook usage
telegram_service = TelegramNotificationService()

def send_telegram_notification(chat_id: str, message: str) -> bool:
    """Send notification via Telegram (for webhook usage)"""
    return telegram_service.send_message(chat_id, message)
