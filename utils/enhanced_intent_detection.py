#!/usr/bin/env python3
"""
Enhanced Intent Detection for Sofi AI
Handles natural language parsing for transfers and other commands
"""

import re
import os
import logging
from typing import Dict, Optional, Tuple
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedIntentDetector:
    """Enhanced intent detection with GPT-powered natural language parsing"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
    
    def extract_transfer_info(self, message: str) -> Optional[Dict]:
        """
        Extract transfer information from natural language using both regex and GPT
        
        Examples:
        - "Send 5k to 1234567891 access bank" -> {amount: 5000, account: "1234567891", bank: "access bank"}
        - "Transfer ₦2000 to 0123456789" -> {amount: 2000, account: "0123456789", bank: None}
        - "8104611794 Opay" -> {account: "8104611794", bank: "Opay"}
        """
        try:            # First try regex-based extraction for common patterns
            regex_result = self._extract_with_regex(message)
            if regex_result:
                return regex_result
            
            # Fallback to GPT for complex natural language
            if self.openai_client:
                return self._extract_with_gpt(message)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting transfer info: {e}")
            return None
    
    def _extract_with_regex(self, message: str) -> Optional[Dict]:
        """Extract transfer info using regex patterns"""
        message = message.lower().strip()
        result = {}
        
        # Extract amount patterns
        amount_patterns = [
            r'(?:send|transfer|pay)\s*(?:₦|ngn)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand)?',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand)\s*(?:to|for)',
            r'₦\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+)\s*(?:k|thousand)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, message)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                # Handle 'k' or 'thousand'
                if 'k' in message or 'thousand' in message:
                    amount *= 1000
                
                result['amount'] = amount
                break
          # Extract account number (10-11 digits) - Improved patterns
        account_patterns = [
            r'\b(\d{10,11})\b',  # 10-11 consecutive digits anywhere
            r'(?:to|send\s+(?:money\s+)?to|transfer\s+(?:to)?)\s*(\d{10,11})',
            r'(\d{10,11})\s*(?:opay|access|gtb|first|zenith|uba|wema|sterling|kuda|palmpay)',
            r'(\d{10,11})\s+(?:access\s+bank|opay|kuda|palmpay)',  # Account + bank name
            r'(?:account\s*(?:number)?:?\s*)?(\d{10,11})'  # With or without "account" prefix
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, message)
            if match:
                result['account'] = match.group(1)
                break
          # Extract bank name - Improved patterns
        bank_patterns = [
            r'\b(opay|access\s*bank|gtbank|gtb|first\s*bank|zenith|uba|wema|sterling|kuda|polaris|palmpay|carbon|vfd|mint)\b',
            r'(\w+)\s*bank',
            r'\d{10,11}\s+(opay|access|gtbank|first|zenith|uba|wema|sterling|kuda|palmpay)',  # Bank after account
            r'\d{10,11}\s+(\w+(?:\s+bank)?)',  # Word(s) after account number
            r'(access\s+bank|first\s+bank|gtbank|zenith\s+bank)'  # Full bank names
        ]
        
        for pattern in bank_patterns:
            match = re.search(pattern, message)
            if match:
                bank = match.group(1).strip()
                # Clean up bank name
                if 'bank' not in bank.lower():
                    bank += ' Bank'
                result['bank'] = bank.title()
                break
        
        # Return result if we found at least account number or amount
        if 'account' in result or 'amount' in result:
            return result
        
        return None
    
    def _extract_with_gpt(self, message: str) -> Optional[Dict]:
        """Extract transfer info using GPT for complex parsing"""
        try:
            prompt = f"""
Extract transfer information from this message: "{message}"

Return JSON with these fields (use null if not found):
- amount: number (convert k/thousand to actual amount, remove currency symbols)
- account: string (10-11 digit account number)
- bank: string (bank name)
- recipient: string (recipient name if mentioned)

Examples:
"Send 5k to 1234567891 access bank" -> {{"amount": 5000, "account": "1234567891", "bank": "Access Bank", "recipient": null}}
"Transfer ₦2000 to 0123456789" -> {{"amount": 2000, "account": "0123456789", "bank": null, "recipient": null}}
"8104611794 Opay mella" -> {{"amount": null, "account": "8104611794", "bank": "Opay", "recipient": "mella"}}

Message: "{message}"
JSON:"""
            
            response = self.openai_client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": "You are a banking assistant that extracts transfer information from messages. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            import json
            result = json.loads(result_text)
            
            # Clean up the result
            if result.get('amount') and isinstance(result['amount'], (int, float)):
                result['amount'] = float(result['amount'])
            
            if result.get('account') and len(str(result['account'])) >= 10:
                result['account'] = str(result['account'])
            
            return result if any(result.values()) else None
            
        except Exception as e:
            logger.error(f"GPT extraction error: {e}")
            return None
    
    def detect_intent_change(self, message: str) -> bool:
        """
        Detect if user wants to change context (exit transfer flow)
        """
        exit_phrases = [
            'cancel', 'stop', 'exit', 'quit', 'balance', 'help',
            'what', 'who', 'when', 'where', 'why', 'how',
            'google', 'weather', 'news', 'joke', 'hello', 'hi'
        ]
        
        message_lower = message.lower().strip()
        
        # Check for question words or exit phrases
        for phrase in exit_phrases:
            if phrase in message_lower:
                return True
        
        # Check for questions (contains ?)
        if '?' in message:
            return True
        
        return False
    
    def is_pure_account_number(self, message: str) -> bool:
        """Check if message is just an account number"""
        cleaned = re.sub(r'[^\d]', '', message)
        return len(cleaned) >= 10 and cleaned.isdigit()

# Global instance
enhanced_intent_detector = EnhancedIntentDetector()
