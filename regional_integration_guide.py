"""
🔧 INTEGRATING REGIONAL EXPRESSIONS INTO SOFI AI

This shows how to enhance your current Sofi AI with Nigerian
regional expression understanding for better user experience.
"""

import os
import json
import openai
from typing import Dict, Any
from nigerian_expressions_database import enhance_message_understanding, detect_intent_with_regional_context

# Enhanced Intent Detection with Regional Support
def enhanced_detect_intent(message: str) -> Dict[str, Any]:
    """
    Enhanced intent detection that understands Nigerian expressions
    
    This replaces/enhances your current detect_intent() function in main.py
    """
    
    # Step 1: Analyze regional context
    regional_analysis = detect_intent_with_regional_context(message)
    enhanced_message = regional_analysis['enhanced_message']
    
    # Step 2: Use enhanced message for OpenAI intent detection
    try:
        from nlp.intent_parser import system_prompt
        
        # Create enhanced system prompt that includes regional context
        enhanced_system_prompt = system_prompt + f"""

REGIONAL CONTEXT ENHANCEMENT:
- Original message: "{message}"
- Enhanced message: "{enhanced_message}" 
- Urgency level: {regional_analysis['urgency_level']}
- Relationship context: {regional_analysis['relationship_context']}
- Contains Nigerian expressions: {regional_analysis['contains_nigerian_expressions']}

Use the enhanced message for intent detection, but preserve the urgency and relationship context in your response.
For urgent transfers, add priority flags. For family transfers, show appropriate care and concern.
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": enhanced_message}  # Use enhanced message
            ],
            temperature=0.3
        )
        
        content = response['choices'][0]['message']['content'].strip()
        parsed_intent = json.loads(content)
        
        # Add regional context to the response
        parsed_intent['regional_context'] = {
            'urgency_level': regional_analysis['urgency_level'],
            'relationship_context': regional_analysis['relationship_context'],
            'original_message': message,
            'enhanced_message': enhanced_message
        }
        
        return parsed_intent
        
    except Exception as e:
        print(f"Error in enhanced intent detection: {e}")
        return {"intent": "general", "details": {}}

# Enhanced AI Reply Generation
async def enhanced_generate_ai_reply(chat_id: str, message: str) -> str:
    """
    Enhanced AI reply that understands and responds to Nigerian expressions
    
    This enhances your current generate_ai_reply() function in main.py
    """
    
    # Analyze regional expressions
    regional_analysis = detect_intent_with_regional_context(message)
    
    # Enhanced system prompt with Nigerian context
    nigerian_enhanced_prompt = """
You are Sofi AI — a friendly, smart, and helpful Nigerian virtual assistant powered by Pip install -ai Tech.

REGIONAL UNDERSTANDING:
You understand Nigerian expressions, Pidgin English, and local ways of speaking about money and banking.
You respond naturally to users whether they speak formal English or use Nigerian expressions.

NIGERIAN EXPRESSIONS YOU UNDERSTAND:
- "Abeg send 5k" = "Please send ₦5,000"
- "My guy" = "My friend" 
- "Sharp sharp" = "Quickly/immediately"
- "Wetin dey my account" = "What's in my account"
- "I wan buy credit" = "I want to buy airtime"
- "Send am" = "Send it"
- "How much I get" = "How much do I have"

RESPONSE STYLE:
- Be warm and conversational like a Nigerian friend
- Use appropriate Nigerian expressions when responding
- Show understanding of urgency when user says "sharp sharp" or "now now"
- Show care when dealing with family transfers
- Be helpful and never sound robotic

When users use Nigerian expressions:
1. Acknowledge you understand them naturally
2. Respond in a mix of standard English and appropriate Nigerian expressions
3. Match their energy level (urgent, casual, formal)
4. Show cultural understanding and warmth
"""
    
    try:
        # Use the enhanced message for better understanding
        enhanced_message = regional_analysis['enhanced_message']
        
        # Add context about the message enhancement
        context_note = ""
        if regional_analysis['contains_nigerian_expressions']:
            context_note = f"\nNote: User used Nigerian expressions. Original: '{message}'"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": nigerian_enhanced_prompt + context_note},
                {"role": "user", "content": enhanced_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_reply = response['choices'][0]['message']['content'].strip()
        
        # If it was an urgent request, add urgency acknowledgment
        if regional_analysis['urgency_level'] == 'urgent':
            ai_reply = "I understand this is urgent! " + ai_reply
        
        return ai_reply
        
    except Exception as e:
        return "Sorry, I'm having trouble understanding right now. Please try again."

# Example Integration Test
def test_regional_integration():
    """Test how the regional expressions work with Sofi's responses"""
    
    print("🧪 TESTING REGIONAL INTEGRATION WITH SOFI AI")
    print("=" * 50)
    
    test_scenarios = [
        {
            "input": "Abeg send 5k give my guy sharp sharp",
            "expected_understanding": "Transfer ₦5,000 to friend urgently",
            "expected_response_style": "Urgent, helpful, understanding"
        },
        {
            "input": "Wetin dey my account? I wan check my kudi",
            "expected_understanding": "Check account balance",
            "expected_response_style": "Natural, Nigerian-friendly"
        },
        {
            "input": "My mama need money for village, send 50k",
            "expected_understanding": "Family transfer, ₦50,000 to mother",
            "expected_response_style": "Caring, family-focused"
        },
        {
            "input": "I wan buy credit sharp sharp, MTN",
            "expected_understanding": "Buy MTN airtime urgently", 
            "expected_response_style": "Quick, efficient"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📱 SCENARIO {i}:")
        print(f"User: '{scenario['input']}'")
        
        # Test intent detection
        intent_result = enhanced_detect_intent(scenario['input'])
        print(f"🎯 Intent: {intent_result.get('intent', 'unknown')}")
        print(f"⚡ Urgency: {intent_result.get('regional_context', {}).get('urgency_level', 'normal')}")
        print(f"👥 Context: {intent_result.get('regional_context', {}).get('relationship_context', 'unknown')}")
        
        print(f"✅ Expected: {scenario['expected_understanding']}")
        print(f"💬 Response Style: {scenario['expected_response_style']}")
        print("-" * 50)

if __name__ == "__main__":
    test_regional_integration()
    
    print("\n🎯 HOW TO INTEGRATE INTO YOUR SOFI AI:")
    print("=" * 50)
    print("1. Replace detect_intent() in main.py with enhanced_detect_intent()")
    print("2. Replace generate_ai_reply() with enhanced_generate_ai_reply()")  
    print("3. Update system prompts to include Nigerian context")
    print("4. Test with Nigerian users for feedback")
    print("5. Continuously expand the expressions database")
    
    print("\n🏆 BENEFITS FOR YOUR USERS:")
    print("=" * 30)
    print("✅ Sofi understands 'Abeg send 5k give my guy'")
    print("✅ Responds to 'Wetin dey my account?'")
    print("✅ Recognizes urgency in 'sharp sharp'")
    print("✅ Shows care for family transfers")
    print("✅ Speaks like a Nigerian friend, not a robot")
    print("✅ Reduces user frustration and confusion")
    print("✅ Makes banking more accessible to all Nigerians")
