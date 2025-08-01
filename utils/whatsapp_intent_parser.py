"""
WhatsApp Intent Parser
Parses user messages to determine intent and extract parameters
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class WhatsAppIntentParser:
    """Parse user intents from WhatsApp messages"""
    
    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            "balance": [
                r"\b(balance|bal|account|wallet)\b",
                r"\b(check|show|what.?s)\s+.*(balance|money|account)",
                r"\b(how much|amount|funds)\b"
            ],
            "send_money": [
                r"\b(send|transfer|give)\s+.*\d+",
                r"\b(pay|send)\s+\w+.*\d+",
                r"\d+.*\b(to|for)\s+\w+",
                r"\b(transfer|send)\s+money"
            ],
            "airtime": [
                r"\b(airtime|recharge|topup|top.?up)\b",
                r"\b(buy|purchase).*airtime",
                r"\b(load|credit).*phone"
            ],
            "crypto": [
                r"\b(crypto|bitcoin|btc|ethereum|eth|usdt)\b",
                r"\b(trade|buy|sell).*crypto",
                r"\b(exchange|swap).*coin"
            ],
            "help": [
                r"\b(help|assist|support|what.*can.*do)\b",
                r"\b(commands|options|features)\b",
                r"\b(how.*work|guide|tutorial)\b"
            ],
            "greeting": [
                r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b",
                r"\b(start|begin|new)\b"
            ]
        }
    
    def parse_intent(self, message: str) -> Dict[str, Any]:
        """
        Parse message and return intent with extracted parameters
        Returns: {
            "intent": str,
            "confidence": float,
            "parameters": dict,
            "raw_message": str
        }
        """
        if not message:
            return self._default_intent(message)
        
        message_lower = message.lower().strip()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    parameters = self._extract_parameters(intent, message)
                    return {
                        "intent": intent,
                        "confidence": 0.8,
                        "parameters": parameters,
                        "raw_message": message
                    }
        
        # No specific intent found, classify as general query
        return {
            "intent": "general",
            "confidence": 0.5,
            "parameters": {},
            "raw_message": message
        }
    
    def _extract_parameters(self, intent: str, message: str) -> Dict[str, Any]:
        """Extract parameters based on intent"""
        parameters = {}
        
        try:
            if intent == "send_money":
                parameters.update(self._extract_money_transfer_params(message))
            elif intent == "airtime":
                parameters.update(self._extract_airtime_params(message))
            elif intent == "crypto":
                parameters.update(self._extract_crypto_params(message))
            
        except Exception as e:
            logger.error(f"Error extracting parameters for {intent}: {e}")
        
        return parameters
    
    def _extract_money_transfer_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters for money transfer"""
        params = {}
        
        # Extract amount
        amount_match = re.search(r'\b(\d{1,3}(?:,?\d{3})*(?:\.\d{2})?)\b', message)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            try:
                params["amount"] = float(amount_str)
            except:
                pass
        
        # Extract recipient name/identifier
        # Look for patterns like "to John", "for Mary", "send Adam"
        recipient_patterns = [
            r'\b(?:to|for)\s+(\w+)',
            r'\bsend\s+(\w+)',
            r'\bgive\s+(\w+)'
        ]
        
        for pattern in recipient_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["recipient"] = match.group(1)
                break
        
        return params
    
    def _extract_airtime_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters for airtime purchase"""
        params = {}
        
        # Extract amount
        amount_match = re.search(r'\b(\d{1,4})\b', message)
        if amount_match:
            try:
                params["amount"] = float(amount_match.group(1))
            except:
                pass
        
        # Extract phone number if provided
        phone_match = re.search(r'\b(0[789]\d{9}|\+234[789]\d{9})\b', message)
        if phone_match:
            params["phone_number"] = phone_match.group(1)
        
        return params
    
    def _extract_crypto_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters for crypto operations"""
        params = {}
        
        # Extract crypto type
        crypto_types = {
            r'\b(bitcoin|btc)\b': 'BTC',
            r'\b(ethereum|eth)\b': 'ETH', 
            r'\b(usdt|tether)\b': 'USDT',
            r'\b(bnb|binance)\b': 'BNB'
        }
        
        for pattern, crypto in crypto_types.items():
            if re.search(pattern, message, re.IGNORECASE):
                params["crypto_type"] = crypto
                break
        
        # Extract operation type
        if re.search(r'\b(buy|purchase)\b', message, re.IGNORECASE):
            params["operation"] = "buy"
        elif re.search(r'\b(sell|convert)\b', message, re.IGNORECASE):
            params["operation"] = "sell"
        elif re.search(r'\b(trade|exchange|swap)\b', message, re.IGNORECASE):
            params["operation"] = "trade"
        
        # Extract amount
        amount_match = re.search(r'\b(\d+(?:\.\d+)?)\b', message)
        if amount_match:
            try:
                params["amount"] = float(amount_match.group(1))
            except:
                pass
        
        return params
    
    def _default_intent(self, message: str) -> Dict[str, Any]:
        """Default intent for unclear messages"""
        return {
            "intent": "unclear",
            "confidence": 0.1,
            "parameters": {},
            "raw_message": message or ""
        }
    
    def get_intent_summary(self, intent_data: Dict[str, Any]) -> str:
        """Get human-readable summary of parsed intent"""
        intent = intent_data.get("intent", "unknown")
        params = intent_data.get("parameters", {})
        
        if intent == "balance":
            return "Balance inquiry"
        elif intent == "send_money":
            amount = params.get("amount", "unknown")
            recipient = params.get("recipient", "unknown")
            return f"Send ₦{amount} to {recipient}"
        elif intent == "airtime":
            amount = params.get("amount", "unknown")
            return f"Buy ₦{amount} airtime"
        elif intent == "crypto":
            operation = params.get("operation", "unknown")
            crypto_type = params.get("crypto_type", "crypto")
            return f"Crypto {operation} - {crypto_type}"
        elif intent == "help":
            return "Help request"
        elif intent == "greeting":
            return "Greeting/Welcome"
        else:
            return f"General query - {intent}"

# Global instance
whatsapp_intent_parser = WhatsAppIntentParser()
