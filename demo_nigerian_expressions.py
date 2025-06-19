#!/usr/bin/env python3
"""
🇳🇬 SOFI AI NIGERIAN EXPRESSIONS DEMO

This script demonstrates how Sofi AI now understands and responds 
to Nigerian expressions, Pidgin English, and local ways of speaking.
"""

import asyncio
from utils.nigerian_expressions import enhance_nigerian_message, get_response_guidance

def demo_nigerian_expressions():
    """Demonstrate Nigerian expressions understanding"""
    print("🇳🇬 SOFI AI - NIGERIAN EXPRESSIONS UNDERSTANDING DEMO")
    print("=" * 65)
    
    # Real-world conversation examples
    conversations = [
        {
            "scenario": "🚀 URGENT TRANSFER TO FRIEND",
            "user_input": "Abeg Sofi, send 10k give my guy sharp sharp! E dey important",
            "description": "User wants to urgently send 10,000 naira to a friend"
        },
        {
            "scenario": "💰 BALANCE INQUIRY IN PIDGIN",
            "user_input": "My account don empty? Wetin remain for my wallet?",
            "description": "User asking about account balance in Pidgin"
        },
        {
            "scenario": "📱 AIRTIME PURCHASE",
            "user_input": "I wan buy credit for 2k, make am fast",
            "description": "User wants to buy 2000 naira airtime quickly"
        },
        {
            "scenario": "👨‍👩‍👧‍👦 FAMILY SUPPORT TRANSFER",
            "user_input": "Transfer 50k give my mama for village now now, na emergency",
            "description": "Emergency transfer to mother in village"
        },
        {
            "scenario": "🏦 ACCOUNT INFORMATION REQUEST",
            "user_input": "Show me my account number make I give my padi",
            "description": "User wants account details to share with friend"
        },
        {
            "scenario": "💸 LARGE AMOUNT TRANSFER",
            "user_input": "Send 1.5m to my brother account for business",
            "description": "Business transfer of 1.5 million naira to brother"
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n{conv['scenario']}")
        print("=" * 50)
        print(f"📝 User says: \"{conv['user_input']}\"")
        print(f"💭 Context: {conv['description']}")
        
        # Analyze the message
        analysis = enhance_nigerian_message(conv['user_input'])
        guidance = get_response_guidance(analysis)
        
        print(f"\n🧠 SOFI'S UNDERSTANDING:")
        print(f"   Enhanced: \"{analysis['enhanced_message']}\"")
        print(f"   Urgency Level: {analysis['urgency_level']}")
        print(f"   Relationship Context: {analysis['relationship_context']}")
        print(f"   Expressions Enhanced: {len(analysis['enhancements'])}")
        
        print(f"\n💬 SOFI'S RESPONSE STYLE:")
        print(f"   Tone: {guidance['tone']}")
        if guidance['urgency_acknowledgment']:
            print(f"   Urgency Note: \"{guidance['urgency_acknowledgment']}\"")
        if guidance['cultural_touch']:
            print(f"   Cultural Touch: \"{guidance['cultural_touch']}\"")
        
        # Generate sample response based on understanding
        sample_response = generate_sample_response(analysis, guidance)
        print(f"\n🤖 SOFI'S LIKELY RESPONSE:")
        print(f"   \"{sample_response}\"")
        
        print("\n" + "-" * 65)

def generate_sample_response(analysis, guidance):
    """Generate a sample response based on analysis and guidance"""
    enhanced_msg = analysis['enhanced_message'].lower()
    urgency = guidance.get('urgency_acknowledgment', '')
    cultural = guidance.get('cultural_touch', '')
    
    # Detect intent type
    if any(word in enhanced_msg for word in ['send', 'transfer', 'give']):
        if analysis['urgency_level'] in ['urgent', 'very_urgent']:
            return f"{urgency}{cultural}I'll help you with that transfer right away! Let me verify the recipient details and we'll get this done immediately."
        else:
            return f"{cultural}I'll help you send that money. Let me verify the recipient account details first."
    
    elif any(word in enhanced_msg for word in ['balance', 'account', 'empty', 'remain']):
        return f"Let me check your account balance right away. I'll also show you your recent transactions."
    
    elif any(word in enhanced_msg for word in ['airtime', 'credit', 'recharge']):
        return f"{urgency}I'll help you buy airtime immediately! Which network would you like to recharge?"
    
    elif any(word in enhanced_msg for word in ['account number', 'account details']):
        return f"Here are your Sofi account details that you can share with your {analysis['relationship_context']}."
    
    else:
        return f"{urgency}{cultural}I understand what you need. Let me help you with that right away!"

def show_expression_categories():
    """Show the categories of Nigerian expressions Sofi understands"""
    print("\n📚 NIGERIAN EXPRESSIONS CATEGORIES SOFI UNDERSTANDS")
    print("=" * 60)
    
    categories = {
        "💰 MONEY TERMS": [
            "kudi → money", "ego → money", "owo → money", 
            "5k → 5000 naira", "2m → 2 million naira", "chicken change → small amount"
        ],
        "📤 TRANSFER TERMS": [
            "send am → send it", "send give → send to", "credit am → send money to him",
            "settle am → pay him", "dash am → give him money", "wire am → transfer it"
        ],
        "💳 BALANCE TERMS": [
            "wetin dey my account → what is in my account", "how much i get → what is my balance",
            "account don empty → account is empty", "my wallet → my account"
        ],
        "⚡ URGENCY TERMS": [
            "sharp sharp → immediately", "now now → right now", 
            "quick quick → very quickly", "make e fast → make it fast"
        ],
        "👥 RELATIONSHIP TERMS": [
            "my guy → my friend", "my padi → my friend", "my person → my friend",
            "my mama → my mother", "my papa → my father"
        ],
        "🗣️ PIDGIN BASICS": [
            "abeg → please", "wetin → what", "dey → is/are", 
            "don → have", "wan → want", "fit → can"
        ]
    }
    
    for category, expressions in categories.items():
        print(f"\n{category}")
        for expr in expressions:
            print(f"   • {expr}")

def main():
    """Run the demonstration"""
    print("🎉 Welcome to Sofi AI's Nigerian Expressions Demo!")
    print("This demo shows how Sofi understands local expressions and responds naturally.")
    print("=" * 80)
    
    # Show expression categories
    show_expression_categories()
    
    # Show conversation demonstrations
    demo_nigerian_expressions()
    
    print("\n🎯 INTEGRATION BENEFITS:")
    print("=" * 40)
    print("✅ Natural conversation in Nigerian English/Pidgin")
    print("✅ Understands local money amounts (5k, 2m, etc.)")
    print("✅ Recognizes urgency levels and relationships")
    print("✅ Responds with appropriate cultural context")
    print("✅ Maintains professional yet friendly Nigerian tone")
    
    print("\n🚀 SOFI AI REGIONAL INTEGRATION COMPLETE!")
    print("Sofi is now ready to serve Nigerian users with full cultural understanding.")

if __name__ == "__main__":
    main()
