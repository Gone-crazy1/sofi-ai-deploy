"""
🇳🇬 NIGERIAN REGIONAL EXPRESSIONS DATABASE
Official integration for Sofi AI

This module enhances Sofi's understanding of Nigerian expressions,
Pidgin English, and local ways of speaking about money and banking.
"""

import re
from typing import Dict, List, Tuple

class NigerianExpressionsDatabase:
    """Database of Nigerian expressions for financial conversations"""
    
    def __init__(self):
        self.expressions = {
            # MONEY/AMOUNT EXPRESSIONS
            "money_terms": {
                "kudi": "money",
                "ego": "money", 
                "owo": "money",
                "change": "money",
                "dough": "money",
                "paper": "money",
                "chicken change": "small amount",
                "peanuts": "very small amount",
                "big money": "large amount"
            },
            
            # TRANSFER/PAYMENT EXPRESSIONS
            "transfer_terms": {
                "send am": "send it",
                "send give": "send to",
                "transfer give": "transfer to", 
                "pay am": "pay him",
                "pay her": "pay her",
                "drop money": "send money",
                "wire am": "transfer it",
                "credit am": "send money to him",
                "credit her": "send money to her",
                "settle am": "pay him",
                "settle her": "pay her",
                "dash am": "give him money",
                "dash her": "give her money"
            },
            
            # BALANCE/ACCOUNT EXPRESSIONS  
            "balance_terms": {
                "how much i get": "what is my balance",
                "wetin dey my account": "what is in my account",
                "how much remain": "what is my remaining balance",
                "my wallet": "my account",
                "account don empty": "account is empty",
                "account don finish": "account is empty",
                "i no get money": "i have no money",
                "money don finish": "money is finished",
                "i broke": "i have no money",
                "see my money": "check my balance"
            },
            
            # URGENCY EXPRESSIONS
            "urgency_terms": {
                "sharp sharp": "immediately",
                "now now": "right now",
                "quick quick": "very quickly",
                "make e fast": "make it fast",
                "no delay": "without delay",
                "urgent": "urgent",
                "emergency": "emergency"
            },
            
            # PERSON/RELATIONSHIP EXPRESSIONS
            "person_terms": {
                "my guy": "my friend",
                "my person": "my friend",
                "my padi": "my friend", 
                "my paddy": "my friend",
                "my brother": "my brother",
                "my sister": "my sister",
                "that guy": "that person",
                "that girl": "that person",
                "my family": "my family member",
                "my papa": "my father",
                "my mama": "my mother",
                "my dad": "my father",
                "my mum": "my mother"
            },
            
            # BANKING EXPRESSIONS
            "banking_terms": {
                "buy credit": "buy airtime",
                "buy data": "buy data bundle",
                "recharge": "buy airtime",
                "top up": "add money",
                "check account": "check balance", 
                "account number": "account number",
                "bank details": "bank information"
            },
            
            # PIDGIN EXPRESSIONS
            "pidgin_terms": {
                "abeg": "please",
                "oya": "okay",
                "na": "is",
                "dey": "is",
                "don": "have",
                "go": "will",
                "wan": "want",
                "fit": "can",
                "sabi": "know",
                "wetin": "what",
                "make": "let",
                "come": "come"
            },
            
            # YORUBA EXPRESSIONS (Southwest Nigeria)
            "yoruba_terms": {
                "owo": "money",
                "bawo": "how much", 
                "elo": "how much",
                "fi ranmi": "send to me",
                "gba": "receive",
                "san": "pay"
            },
            
            # IGBO EXPRESSIONS (Southeast Nigeria)  
            "igbo_terms": {
                "ego": "money",
                "ole": "how much",
                "zipu": "send", 
                "kwuo": "pay",
                "nata": "receive"
            },
            
            # HAUSA EXPRESSIONS (Northern Nigeria)
            "hausa_terms": {
                "kudi": "money",
                "nawa": "how much",
                "aika": "send",
                "karba": "receive", 
                "biya": "pay"
            }
        }
        
        # Amount patterns (k = thousand, m = million)
        self.amount_patterns = {
            "k_amounts": {
                r'\b(\d+)k\b': lambda m: f"{int(m.group(1)) * 1000} naira",
                r'\b(\d+\.\d+)k\b': lambda m: f"{int(float(m.group(1)) * 1000)} naira"
            },
            "m_amounts": {
                r'\b(\d+)m\b': lambda m: f"{int(m.group(1)) * 1000000} naira",
                r'\b(\d+\.\d+)m\b': lambda m: f"{int(float(m.group(1)) * 1000000)} naira"
            }
        }
        
        # Context patterns for understanding relationships and urgency
        self.context_patterns = {
            "urgent_keywords": [
                "emergency", "urgent", "sharp sharp", "now now", "quick quick",
                "fast", "immediately", "asap", "rush"
            ],
            "family_keywords": [
                "papa", "mama", "father", "mother", "brother", "sister", 
                "family", "home", "village", "parents"
            ],
            "friend_keywords": [
                "guy", "padi", "paddy", "person", "friend", "mate"
            ]
        }
    
    def enhance_message(self, message: str) -> Dict[str, any]:
        """
        Enhance a message by translating Nigerian expressions to standard English
        
        Returns:
            Dict with enhanced_message, urgency_level, relationship_context, etc.
        """
        original_message = message
        enhanced = message.lower()
        
        # Track what was enhanced
        enhancements = []
        
        # Step 1: Replace amount patterns (5k -> 5000 naira)
        for pattern_type, patterns in self.amount_patterns.items():
            for pattern, replacement_func in patterns.items():
                if re.search(pattern, enhanced):
                    enhanced = re.sub(pattern, replacement_func, enhanced)
                    enhancements.append(f"Amount pattern: {pattern_type}")
        
        # Step 2: Replace Nigerian expressions with English equivalents
        for category, expressions in self.expressions.items():
            for nigerian_expr, english_expr in expressions.items():
                if nigerian_expr in enhanced:
                    enhanced = enhanced.replace(nigerian_expr, english_expr)
                    enhancements.append(f"Expression: {nigerian_expr} -> {english_expr}")
        
        # Step 3: Detect context
        urgency_level = self._detect_urgency(original_message)
        relationship_context = self._detect_relationship(original_message)
        
        return {
            "original_message": original_message,
            "enhanced_message": enhanced,
            "urgency_level": urgency_level,
            "relationship_context": relationship_context,
            "enhancements": enhancements,
            "contains_nigerian_expressions": len(enhancements) > 0
        }
    
    def _detect_urgency(self, message: str) -> str:
        """Detect urgency level from message"""
        message_lower = message.lower()
        
        urgent_count = sum(1 for keyword in self.context_patterns["urgent_keywords"] 
                          if keyword in message_lower)
        
        if urgent_count >= 2:
            return "very_urgent"
        elif urgent_count >= 1:
            return "urgent"
        else:
            return "normal"
    
    def _detect_relationship(self, message: str) -> str:
        """Detect relationship context from message"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in self.context_patterns["family_keywords"]):
            return "family"
        elif any(keyword in message_lower for keyword in self.context_patterns["friend_keywords"]):
            return "friend"
        else:
            return "unknown"
    
    def get_response_style_guidance(self, analysis: Dict) -> Dict[str, str]:
        """
        Get guidance on how Sofi should respond based on the analysis
        """
        guidance = {
            "tone": "friendly",
            "urgency_acknowledgment": "",
            "cultural_touch": ""
        }
        
        # Adjust based on urgency
        if analysis["urgency_level"] == "very_urgent":
            guidance["urgency_acknowledgment"] = "I understand this is very urgent! "
            guidance["tone"] = "urgent_helpful"
        elif analysis["urgency_level"] == "urgent":
            guidance["urgency_acknowledgment"] = "I see this is urgent. "
            guidance["tone"] = "prompt_helpful"
        
        # Adjust based on relationship
        if analysis["relationship_context"] == "family":
            guidance["cultural_touch"] = "Taking care of family is important. "
            guidance["tone"] = "caring"
        elif analysis["relationship_context"] == "friend":
            guidance["cultural_touch"] = "I'll help you sort out your friend. "
        
        return guidance

# Global instance
nigerian_db = NigerianExpressionsDatabase()

def enhance_nigerian_message(message: str) -> Dict[str, any]:
    """
    Main function to enhance messages with Nigerian expression understanding
    """
    return nigerian_db.enhance_message(message)

def get_response_guidance(analysis: Dict) -> Dict[str, str]:
    """
    Get guidance on how to respond to enhanced messages
    """
    return nigerian_db.get_response_style_guidance(analysis)

# Test the enhancement
if __name__ == "__main__":
    test_messages = [
        "Abeg send 5k give my guy sharp sharp",
        "My account don empty, wetin remain?",
        "I wan buy credit for my phone",
        "Transfer 50k give my mama for village now now",
        "How much ego I get for my wallet?"
    ]
    
    print("🇳🇬 TESTING NIGERIAN EXPRESSIONS DATABASE")
    print("=" * 50)
    
    for message in test_messages:
        result = enhance_nigerian_message(message)
        guidance = get_response_guidance(result)
        
        print(f"\n📝 Original: '{message}'")
        print(f"✅ Enhanced: '{result['enhanced_message']}'")
        print(f"⚡ Urgency: {result['urgency_level']}")
        print(f"👥 Context: {result['relationship_context']}")
        print(f"💬 Response Tone: {guidance['tone']}")
        if guidance['urgency_acknowledgment']:
            print(f"🚨 Urgency Note: {guidance['urgency_acknowledgment']}")
        if guidance['cultural_touch']:
            print(f"🇳🇬 Cultural Touch: {guidance['cultural_touch']}")
        print("-" * 40)
