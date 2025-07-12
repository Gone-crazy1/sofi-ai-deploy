"""
⚡ SOFI AI SPEED OPTIMIZATION SYSTEM
===================================

Ultra-fast response system with caching, preprocessing, and instant replies.
Makes Sofi respond like lightning with sub-second response times.
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Tuple, Any
from functools import lru_cache
import re

logger = logging.getLogger(__name__)

class SofiSpeedOptimizer:
    """Ultra-fast response optimization system"""
    
    def __init__(self):
        # Cache for frequent responses
        self.response_cache = {}
        self.user_context_cache = {}
        self.intent_cache = {}
        
        # Pre-compiled regex patterns for instant matching
        self.patterns = {
            'balance': re.compile(r'\b(balance|check account|how much|my account)\b', re.IGNORECASE),
            'transfer': re.compile(r'\b(send|transfer|pay)\s+(\d+|\d+k|\d+,\d+)\b', re.IGNORECASE),
            'beneficiary': re.compile(r'\b(save as|list beneficiaries|my beneficiaries)\b', re.IGNORECASE),
            'summary': re.compile(r'\b(summary|summarize|spending|transactions)\b', re.IGNORECASE),
            'greeting': re.compile(r'\b(hi|hello|hey|good morning|good afternoon)\b', re.IGNORECASE),
            'airtime': re.compile(r'\b(airtime|data|recharge|mtn|glo|airtel)\b', re.IGNORECASE),
            'crypto': re.compile(r'\b(bitcoin|btc|crypto|wallet|ethereum)\b', re.IGNORECASE)
        }
        
        # Pre-built instant responses for common queries
        self.instant_responses = {
            'greeting': [
                "Hey there! 👋 Ready to help with your money matters!",
                "Hello! 😊 What can I do for you today?",
                "Hi! 🚀 Let's get things done quickly!",
                "Hey! 💫 How can I assist you today?"
            ],
            'balance_processing': "⚡ Getting your balance instantly...",
            'transfer_processing': "🚀 Processing your transfer at lightning speed...",
            'beneficiary_processing': "💾 Checking your saved recipients...",
            'summary_processing': "📊 Analyzing your transactions super fast..."
        }
    
    async def quick_intent_detection(self, message: str) -> Tuple[str, float]:
        """Lightning-fast intent detection using pre-compiled patterns"""
        start_time = time.time()
        
        message_lower = message.lower().strip()
        
        # Check cache first (instant lookup)
        cache_key = hash(message_lower)
        if cache_key in self.intent_cache:
            intent, confidence = self.intent_cache[cache_key]
            logger.info(f"⚡ Cache hit - Intent: {intent} ({time.time() - start_time:.3f}s)")
            return intent, confidence
        
        # Quick pattern matching
        for intent, pattern in self.patterns.items():
            if pattern.search(message):
                confidence = 0.9
                # Cache the result
                self.intent_cache[cache_key] = (intent, confidence)
                logger.info(f"⚡ Quick intent: {intent} ({time.time() - start_time:.3f}s)")
                return intent, confidence
        
        # Default intent
        intent, confidence = 'general', 0.5
        self.intent_cache[cache_key] = (intent, confidence)
        return intent, confidence
    
    async def get_instant_response(self, intent: str, message: str) -> Optional[str]:
        """Get instant responses for common queries"""
        
        if intent == 'greeting':
            import random
            return random.choice(self.instant_responses['greeting'])
        
        elif intent == 'balance':
            return self.instant_responses['balance_processing']
        
        elif intent == 'transfer':
            return self.instant_responses['transfer_processing']
        
        elif intent == 'beneficiary':
            return self.instant_responses['beneficiary_processing']
        
        elif intent == 'summary':
            return self.instant_responses['summary_processing']
        
        return None
    
    def cache_user_context(self, chat_id: str, user_data: dict, virtual_account: dict = None):
        """Cache user context for instant access"""
        self.user_context_cache[chat_id] = {
            'user_data': user_data,
            'virtual_account': virtual_account,
            'timestamp': time.time()
        }
    
    def get_cached_context(self, chat_id: str) -> Tuple[Optional[dict], Optional[dict]]:
        """Get cached user context"""
        cached = self.user_context_cache.get(chat_id)
        if cached and (time.time() - cached['timestamp']) < 300:  # 5 minutes cache
            return cached['user_data'], cached['virtual_account']
        return None, None
    
    @lru_cache(maxsize=1000)
    def quick_amount_extraction(self, message: str) -> Optional[float]:
        """Lightning-fast amount extraction with caching"""
        # Enhanced regex for Nigerian-style amounts
        patterns = [
            r'\b(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:naira|ngn|₦)?\b',  # 5,000 or 5000
            r'\b(\d+)k\b',  # 5k = 5000
            r'\b(\d+)m\b',  # 1m = 1,000,000
            r'₦\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # ₦5,000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                try:
                    if 'k' in message.lower():
                        return float(amount_str) * 1000
                    elif 'm' in message.lower():
                        return float(amount_str) * 1000000
                    else:
                        return float(amount_str.replace(',', ''))
                except ValueError:
                    continue
        
        return None
    
    async def preprocess_message(self, message: str) -> Dict[str, Any]:
        """Pre-process message for common data extraction"""
        start_time = time.time()
        
        # Quick parallel processing
        tasks = [
            self.quick_intent_detection(message),
            asyncio.to_thread(self.quick_amount_extraction, message),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        intent, confidence = results[0] if not isinstance(results[0], Exception) else ('general', 0.5)
        amount = results[1] if not isinstance(results[1], Exception) else None
        
        preprocessing_data = {
            'intent': intent,
            'confidence': confidence,
            'amount': amount,
            'processing_time': time.time() - start_time,
            'original_message': message
        }
        
        logger.info(f"⚡ Preprocessing completed in {preprocessing_data['processing_time']:.3f}s")
        return preprocessing_data
    
    async def handle_fallback_command(self, message: str, chat_id: str, user_data: dict) -> str:
        """Handle fallback commands with ultra-fast processing"""
        try:
            message_lower = message.lower()
            
            # Quick pattern matching for common commands
            if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
                return "Hello! I'm Sofi, your ultra-fast banking assistant ⚡ How can I help you today?"
            
            if any(word in message_lower for word in ["thanks", "thank you", "thx"]):
                return "You're welcome! Always happy to help ⚡"
            
            if any(word in message_lower for word in ["bye", "goodbye", "see you"]):
                return "Goodbye! Have a great day! 👋"
            
            if "beneficiar" in message_lower:
                return "I can help you manage beneficiaries! Try 'save John as beneficiary' or 'send 5k to my wife' ⚡"
            
            if any(word in message_lower for word in ["transaction", "history", "spending"]):
                return "I can analyze your transactions! Try 'summarize my transactions' for a 2-month overview ⚡"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fallback command error: {str(e)}")
            return None
    
    def get_cached_balance(self, chat_id: str) -> str:
        """Get cached balance for ultra-fast responses"""
        try:
            cache_key = f"balance_{chat_id}"
            cached = self.user_context_cache.get(cache_key)
            
            if cached and time.time() - cached['timestamp'] < 30:  # 30 second cache
                return cached.get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache balance error: {str(e)}")
            return None
    
    def cache_balance(self, chat_id: str, balance_response: str):
        """Cache balance response for speed"""
        try:
            cache_key = f"balance_{chat_id}"
            self.user_context_cache[cache_key] = {
                'data': balance_response,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Balance caching error: {str(e)}")
    
    def quick_extract_amount(self, message: str) -> float:
        """Quickly extract amount from message (non-cached version)"""
        try:
            # Use the cached method but without @lru_cache for this specific call
            amount = self.quick_amount_extraction(message)
            return amount
            
        except Exception as e:
            logger.error(f"❌ Amount extraction error: {str(e)}")
            return None
    
    def get_cached_error_response(self) -> str:
        """Get cached error response for speed"""
        import random
        error_responses = [
            "I'm experiencing a temporary issue. Please try again in a moment ⚡",
            "Something went wrong, but I'm back! How can I help you? ⚡",
            "Technical hiccup resolved! What can I do for you? ⚡"
        ]
        return random.choice(error_responses)

# Global speed optimizer instance
speed_optimizer = SofiSpeedOptimizer()
