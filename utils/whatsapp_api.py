"""
WhatsApp API Helper for Read Receipts and Typing Indicators
Implements message reading and typing status for better UX
"""

import logging
import requests
import time
import asyncio
from typing import Optional
import os

logger = logging.getLogger(__name__)

class WhatsAppAPI:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
        if not self.access_token or not self.phone_number_id:
            logger.error("❌ WhatsApp credentials not configured")
    
    def _get_headers(self):
        """Get headers for WhatsApp API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a WhatsApp message as read (shows blue checkmarks)
        
        Args:
            message_id (str): The ID of the message to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📨 Marking message {message_id} as read")
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Message {message_id} marked as read")
                return True
            else:
                logger.error(f"❌ Failed to mark message as read: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marking message as read: {e}")
            return False
    
    async def send_typing_indicator(self, phone_number: str, duration: float = 2.0) -> bool:
        """
        Show typing indicator in WhatsApp chat by sending a temporary message
        
        Args:
            phone_number (str): The recipient's phone number
            duration (float): How long to show typing (seconds)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"⌨️ Simulating typing indicator to {phone_number} for {duration}s")
            
            # Send a temporary "typing..." message
            typing_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": "⌨️ Sofi is typing..."
                }
            }
            
            # Send the typing message
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=typing_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Typing indicator sent to {phone_number}")
                
                # Wait for the specified duration
                await asyncio.sleep(duration)
                
                # Send a "delete" or "correction" by sending empty message to clear typing
                clear_payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual", 
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": "🤖 Processing..."
                    }
                }
                
                # Send processing message
                requests.post(
                    f"{self.base_url}/messages",
                    headers=self._get_headers(),
                    json=clear_payload,
                    timeout=5
                )
                
                # Brief pause before actual response
                await asyncio.sleep(0.5)
                
                return True
            else:
                logger.error(f"❌ Failed to send typing indicator: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error showing typing indicator: {e}")
            return False
            
            logger.info(f"✅ Typing simulation completed for {phone_number}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error showing typing indicator: {e}")
            return False
    
    async def send_message_with_read_and_typing(self, phone_number: str, message: str, 
                                               message_id_to_read: Optional[str] = None,
                                               typing_duration: float = 2.0) -> bool:
        """
        Send a message with proper read receipt and realistic typing simulation
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message to send
            message_id_to_read (str, optional): Message ID to mark as read
            typing_duration (float): How long to show typing
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Step 1: Mark incoming message as read (blue checkmarks)
            if message_id_to_read:
                await self.mark_message_as_read(message_id_to_read)
                await asyncio.sleep(0.3)  # Brief pause after reading
            
            # Step 2: Show realistic typing indicator
            logger.info(f"🤖 Starting realistic typing simulation for {phone_number}")
            
            # Send "Sofi is typing..." message
            typing_msg = await self.send_text_message(phone_number, "⌨️ Sofi is typing...")
            
            # Pause to simulate thinking/typing time
            await asyncio.sleep(typing_duration)
            
            # Step 3: Send the actual response
            logger.info(f"📤 Sending actual response to {phone_number}")
            return await self.send_text_message(phone_number, message)
            
        except Exception as e:
            logger.error(f"❌ Error in send_message_with_read_and_typing: {e}")
            # Fallback: just send the message
            return await self.send_text_message(phone_number, message)
    
    async def send_text_message(self, phone_number: str, message: str) -> bool:
        """
        Send a text message via WhatsApp
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📤 Sending message to {phone_number}")
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

# Global instance
whatsapp_api = WhatsAppAPI()
