"""
WhatsApp Media Processing Utilities
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

def process_whatsapp_media(message):
    """Process WhatsApp media messages (images, documents, etc.)"""
    try:
        message_type = message.get("type")
        
        if message_type == "image":
            image_data = message.get("image", {})
            media_id = image_data.get("id")
            caption = image_data.get("caption", "")
            
            # For now, return a simple response
            return True, f"📸 Image received: {caption if caption else 'Processing your image...'}"
            
        elif message_type == "document":
            doc_data = message.get("document", {})
            filename = doc_data.get("filename", "document")
            
            return True, f"📄 Document received: {filename}"
            
        else:
            return False, f"❌ Unsupported media type: {message_type}"
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp media: {e}")
        return False, "❌ Error processing media"

def process_whatsapp_voice(message):
    """Process WhatsApp voice messages"""
    try:
        voice_data = message.get("audio", {}) or message.get("voice", {})
        
        if voice_data:
            return True, "🎤 Voice message received. Voice processing not yet implemented for WhatsApp."
        else:
            return False, "❌ No voice data found"
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp voice: {e}")
        return False, "❌ Error processing voice message"

def download_whatsapp_media(media_id):
    """Download media from WhatsApp using media ID"""
    try:
        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        
        # Get media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            media_data = response.json()
            media_url = media_data.get("url")
            
            if media_url:
                # Download the actual media file
                media_response = requests.get(media_url, headers=headers)
                if media_response.status_code == 200:
                    return True, media_response.content
                    
        return False, "Failed to download media"
        
    except Exception as e:
        logger.error(f"Error downloading WhatsApp media: {e}")
        return False, f"Error: {e}"
