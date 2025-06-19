"""
🇳🇬 NIGERIAN REGIONAL EXPRESSIONS DATABASE

This database helps Sofi understand how Nigerians actually speak
when discussing money, banking, and financial transactions.

CATEGORIES:
1. Money/Amount Expressions
2. Transfer/Payment Expressions  
3. Balance/Account Expressions
4. Urgency/Time Expressions
5. Person/Relationship Expressions
6. General Banking Expressions
"""

# Nigerian Regional Expressions Database
NIGERIAN_EXPRESSIONS = {
    
    # MONEY/AMOUNT EXPRESSIONS
    "money_expressions": {
        "kudi": "money",
        "ego": "money", 
        "owo": "money",
        "change": "money",
        "dough": "money",
        "paper": "money",
        "5k": "5000 naira",
        "10k": "10000 naira", 
        "50k": "50000 naira",
        "100k": "100000 naira",
        "1m": "1000000 naira",
        "small money": "little amount",
        "big money": "large amount",
        "chicken change": "small amount",
        "peanuts": "very small amount"
    },
    
    # TRANSFER/PAYMENT EXPRESSIONS
    "transfer_expressions": {
        "send am": "send it",
        "send give": "send to",
        "transfer give": "transfer to", 
        "pay am": "pay him/her",
        "drop money": "send money",
        "wire am": "transfer it",
        "credit am": "send money to him/her",
        "settle am": "pay him/her",
        "dash am": "give him/her money",
        "send sharp sharp": "send quickly",
        "send now now": "send immediately",
        "abeg send": "please send"
    },
    
    # BALANCE/ACCOUNT EXPRESSIONS  
    "balance_expressions": {
        "how much I get": "what's my balance",
        "wetin dey my account": "what's in my account",
        "my account balance": "account balance",
        "how much remain": "remaining balance",
        "my wallet": "my account",
        "my account don empty": "my account is empty",
        "I no get money": "I don't have money",
        "money don finish": "money is finished",
        "I broke": "I have no money"
    },
    
    # URGENCY/TIME EXPRESSIONS
    "urgency_expressions": {
        "sharp sharp": "quickly/immediately",
        "now now": "right now",
        "asap": "as soon as possible", 
        "urgent": "urgent",
        "quick quick": "very quickly",
        "make e fast": "make it fast",
        "no delay": "without delay",
        "immediately": "immediately"
    },
    
    # PERSON/RELATIONSHIP EXPRESSIONS
    "person_expressions": {
        "my guy": "my friend",
        "my person": "my friend/person",
        "my padi": "my friend", 
        "my brother": "my brother/friend",
        "my sister": "my sister/friend",
        "that guy": "that person",
        "the person": "the person",
        "my family": "my family member",
        "my papa": "my father",
        "my mama": "my mother"
    },
    
    # GENERAL BANKING EXPRESSIONS
    "banking_expressions": {
        "buy credit": "buy airtime",
        "buy data": "buy data bundle",
        "recharge": "buy airtime",
        "top up": "add money/airtime",
        "check account": "check balance", 
        "see my money": "check balance",
        "account number": "account number",
        "bank details": "bank information",
        "transaction": "transaction",
        "receipt": "receipt/proof"
    },
    
    # NIGERIAN PIDGIN PHRASES
    "pidgin_phrases": {
        "abeg": "please",
        "oya": "come on/okay",
        "na": "it is/that's",
        "dey": "is/are",
        "don": "have/has",
        "go": "will",
        "wan": "want",
        "fit": "can",
        "sabi": "know",
        "wetin": "what"
    },
    
    # YORUBA EXPRESSIONS (Lagos/Southwest)
    "yoruba_expressions": {
        "owo": "money",
        "bawo": "how much", 
        "elo": "how much",
        "fi ranmi": "send to me",
        "gba": "receive",
        "san": "pay"
    },
    
    # IGBO EXPRESSIONS (Southeast)  
    "igbo_expressions": {
        "ego": "money",
        "ole": "how much",
        "zipu": "send", 
        "kwuo": "pay",
        "nata": "receive"
    },
    
    # HAUSA EXPRESSIONS (North)
    "hausa_expressions": {
        "kudi": "money",
        "nawa": "how much",
        "aika": "send",
        "karba": "receive", 
        "biya": "pay"
    }
}

# Context patterns for better understanding
CONTEXT_PATTERNS = {
    "urgent_transfer": [
        "emergency", "urgent", "sharp sharp", "now now", "asap",
        "quick quick", "fast", "immediately"
    ],
    
    "family_transfer": [
        "my papa", "my mama", "my brother", "my sister", 
        "family", "home", "village"
    ],
    
    "friend_transfer": [
        "my guy", "my padi", "my person", "friend",
        "school mate", "work mate"
    ],
    
    "business_transfer": [
        "supplier", "vendor", "shop", "business",
        "payment", "invoice", "debt"
    ]
}

# Amount interpretation rules
AMOUNT_PATTERNS = {
    "k_amounts": {
        "5k": 5000, "10k": 10000, "20k": 20000, "50k": 50000,
        "100k": 100000, "200k": 200000, "500k": 500000
    },
    
    "m_amounts": {
        "1m": 1000000, "2m": 2000000, "5m": 5000000
    },
    
    "written_amounts": {
        "five thousand": 5000,
        "ten thousand": 10000, 
        "twenty thousand": 20000,
        "fifty thousand": 50000,
        "one hundred thousand": 100000
    }
}

def enhance_message_understanding(message: str) -> str:
    """
    Enhance message understanding using Nigerian expressions
    
    Example:
    Input: "Abeg send 5k give my guy sharp sharp"
    Output: "Please send 5000 naira to my friend quickly"
    """
    enhanced = message.lower()
    
    # Replace Nigerian expressions with standard English
    for category, expressions in NIGERIAN_EXPRESSIONS.items():
        for nigerian_expr, english_expr in expressions.items():
            enhanced = enhanced.replace(nigerian_expr, english_expr)
    
    # Handle amount patterns
    for pattern_type, amounts in AMOUNT_PATTERNS.items():
        for nigerian_amount, actual_amount in amounts.items():
            enhanced = enhanced.replace(nigerian_amount, f"{actual_amount} naira")
    
    return enhanced

def detect_intent_with_regional_context(message: str) -> dict:
    """
    Detect intent with Nigerian regional context
    
    This would work alongside the existing OpenAI intent detection
    to provide better understanding of Nigerian expressions.
    """
    enhanced_message = enhance_message_understanding(message)
    
    # Detect urgency
    urgency_level = "normal"
    if any(urgent_word in message.lower() for urgent_word in CONTEXT_PATTERNS["urgent_transfer"]):
        urgency_level = "urgent"
    
    # Detect relationship context
    relationship_context = "unknown"
    if any(family_word in message.lower() for family_word in CONTEXT_PATTERNS["family_transfer"]):
        relationship_context = "family"
    elif any(friend_word in message.lower() for friend_word in CONTEXT_PATTERNS["friend_transfer"]):
        relationship_context = "friend"
    elif any(business_word in message.lower() for business_word in CONTEXT_PATTERNS["business_transfer"]):
        relationship_context = "business"
    
    return {
        "original_message": message,
        "enhanced_message": enhanced_message,
        "urgency_level": urgency_level,
        "relationship_context": relationship_context,
        "contains_nigerian_expressions": enhanced_message != message.lower()
    }

# Example usage and testing
if __name__ == "__main__":
    
    print("🇳🇬 NIGERIAN REGIONAL EXPRESSIONS DATABASE")
    print("=" * 50)
    
    # Test messages
    test_messages = [
        "Abeg send 5k give my guy sharp sharp",
        "My account don empty, wetin remain?",
        "I wan buy credit for my phone",
        "Send am now now, na emergency",
        "How much ego I get for my wallet?",
        "Transfer 50k give my mama for village",
        "My padi need money urgent, send 20k"
    ]
    
    print("🧪 TESTING EXPRESSION UNDERSTANDING:")
    print("-" * 40)
    
    for message in test_messages:
        result = detect_intent_with_regional_context(message)
        
        print(f"📝 Original: '{message}'")
        print(f"✅ Enhanced: '{result['enhanced_message']}'")
        print(f"⚡ Urgency: {result['urgency_level']}")
        print(f"👥 Context: {result['relationship_context']}")
        print(f"🇳🇬 Nigerian: {'Yes' if result['contains_nigerian_expressions'] else 'No'}")
        print("-" * 40)
    
    print("\n🏆 BENEFITS OF REGIONAL DATABASE:")
    print("• Better understanding of Nigerian users")
    print("• More natural conversation experience")
    print("• Reduced misunderstandings") 
    print("• Cultural sensitivity and inclusivity")
    print("• Support for multiple Nigerian languages")
