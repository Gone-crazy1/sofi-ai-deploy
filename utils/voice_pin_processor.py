#!/usr/bin/env python3
"""
🎙️ VOICE PIN VERIFICATION SYSTEM
=====================================
Handles voice note PIN verification for Sofi AI transfers.
Users can send voice notes with their 4-digit PIN instead of using the web app.
"""

import os
import logging
import requests
import speech_recognition as sr
import io
from typing import Dict, Optional, List
import re
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

class VoicePinProcessor:
    """Processes voice notes to extract PIN digits"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Common digit pronunciations in different accents
        self.digit_patterns = {
            '0': ['zero', 'oh', 'o'],
            '1': ['one', 'wan'],
            '2': ['two', 'tu'],
            '3': ['three', 'tree'],
            '4': ['four', 'for'],
            '5': ['five', 'fife'],
            '6': ['six', 'siks'],
            '7': ['seven', 'seben'],
            '8': ['eight', 'ait'],
            '9': ['nine', 'nain']
        }
    
    async def download_voice_file(self, file_url: str, bot_token: str) -> Optional[bytes]:
        """Download voice file from Telegram servers"""
        try:
            # Get file info from Telegram
            file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_url}"
            file_info_response = requests.get(file_info_url)
            
            if file_info_response.status_code != 200:
                logger.error("Failed to get file info from Telegram")
                return None
            
            file_info = file_info_response.json()
            if not file_info.get('ok'):
                logger.error(f"Telegram API error: {file_info}")
                return None
            
            file_path = file_info['result']['file_path']
            
            # Download the actual file
            download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            download_response = requests.get(download_url)
            
            if download_response.status_code == 200:
                logger.info("✅ Voice file downloaded successfully")
                return download_response.content
            else:
                logger.error(f"Failed to download voice file: {download_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading voice file: {e}")
            return None
    
    def convert_audio_for_speech_recognition(self, audio_data: bytes) -> Optional[bytes]:
        """Convert audio to format suitable for speech recognition"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load with pydub and convert to WAV
            audio = AudioSegment.from_file(temp_file_path)
            
            # Convert to mono, 16kHz for better speech recognition
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Export as WAV
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return wav_data
            
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return None
    
    def extract_digits_from_text(self, text: str) -> Optional[str]:
        """Extract 4-digit PIN from transcribed text"""
        try:
            text = text.lower().strip()
            logger.info(f"🎙️ Transcribed text: '{text}'")
            
            # Method 1: Look for 4 consecutive digits
            digit_match = re.search(r'\b\d{4}\b', text)
            if digit_match:
                pin = digit_match.group()
                logger.info(f"✅ Found 4-digit PIN: {pin}")
                return pin
            
            # Method 2: Extract individual spoken digits
            extracted_digits = []
            words = text.split()
            
            for word in words:
                # Check if word is a digit
                if word.isdigit() and len(word) == 1:
                    extracted_digits.append(word)
                else:
                    # Check against digit patterns
                    for digit, patterns in self.digit_patterns.items():
                        if word in patterns:
                            extracted_digits.append(digit)
                            break
            
            # If we found exactly 4 digits, return as PIN
            if len(extracted_digits) == 4:
                pin = ''.join(extracted_digits)
                logger.info(f"✅ Extracted PIN from words: {pin}")
                return pin
            
            # Method 3: Look for any 4 digits in sequence (even with spaces)
            all_digits = re.findall(r'\d', text)
            if len(all_digits) >= 4:
                pin = ''.join(all_digits[:4])
                logger.info(f"✅ Found PIN from digit sequence: {pin}")
                return pin
            
            logger.warning(f"❌ Could not extract 4-digit PIN from: '{text}'")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting digits: {e}")
            return None
    
    async def process_voice_pin(self, file_id: str, bot_token: str) -> Dict[str, any]:
        """
        Process voice note and extract PIN
        
        Args:
            file_id: Telegram file ID for the voice note
            bot_token: Telegram bot token
            
        Returns:
            Dict with success status and extracted PIN or error message
        """
        try:
            logger.info(f"🎙️ Processing voice PIN for file_id: {file_id}")
            
            # Download voice file
            audio_data = await self.download_voice_file(file_id, bot_token)
            if not audio_data:
                return {
                    "success": False,
                    "error": "Could not download voice file"
                }
            
            # Convert audio for speech recognition
            wav_data = self.convert_audio_for_speech_recognition(audio_data)
            if not wav_data:
                return {
                    "success": False,
                    "error": "Could not process audio file"
                }
            
            # Perform speech recognition
            with sr.AudioFile(io.BytesIO(wav_data)) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                audio = self.recognizer.record(source)
                
                # Try Google Speech Recognition (free tier)
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    logger.info(f"🎙️ Speech recognition successful: '{text}'")
                except sr.UnknownValueError:
                    # Try with Nigerian English if US English fails
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-NG')
                        logger.info(f"🎙️ Speech recognition (NG) successful: '{text}'")
                    except sr.UnknownValueError:
                        return {
                            "success": False,
                            "error": "Could not understand the voice note. Please speak clearly and say your 4-digit PIN."
                        }
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {e}")
                    return {
                        "success": False,
                        "error": "Speech recognition service temporarily unavailable. Please use the web app instead."
                    }
            
            # Extract PIN from transcribed text
            pin = self.extract_digits_from_text(text)
            
            if pin and len(pin) == 4 and pin.isdigit():
                return {
                    "success": True,
                    "pin": pin,
                    "transcribed_text": text
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not extract a 4-digit PIN from your voice. I heard: '{text}'. Please say your PIN clearly as four separate digits."
                }
                
        except Exception as e:
            logger.error(f"Error processing voice PIN: {e}")
            return {
                "success": False,
                "error": "An error occurred while processing your voice note. Please try again or use the web app."
            }

# Global instance
voice_pin_processor = VoicePinProcessor()

async def process_voice_pin_message(file_id: str, bot_token: str) -> Dict[str, any]:
    """
    Main function to process voice PIN messages
    
    Args:
        file_id: Telegram voice file ID
        bot_token: Telegram bot token
        
    Returns:
        Dict with processing result
    """
    return await voice_pin_processor.process_voice_pin(file_id, bot_token)
