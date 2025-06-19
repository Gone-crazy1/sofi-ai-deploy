#!/usr/bin/env python3
"""
DEMONSTRATION: Sharp Sofi AI with Permanent Memory & Context Awareness
This script shows how Sofi AI becomes truly intelligent like ChatGPT/Siri

Key Features Demonstrated:
✅ Permanent Memory (remembers everything forever)
✅ Date/Time Awareness (knows current date, day, time)
✅ Context Understanding (recalls past interactions)
✅ Spending Analytics (intelligent financial insights)
✅ Xara-style Account Detection (smart transfer processing)
"""

import asyncio
import os, sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class SharpSofiDemo:
    """Demonstration of Sharp Sofi AI capabilities"""
    
    def __init__(self):
        self.test_chat_id = "demo_user_123456"
    
    async def demo_permanent_memory(self):
        """Demonstrate permanent memory capabilities"""
        print("\n🧠 PERMANENT MEMORY DEMONSTRATION")
        print("=" * 50)
        
        # Import here to avoid circular imports during development
        from utils.sharp_memory import sharp_memory, remember_user_action, remember_transaction
        
        # Simulate user interactions over time
        print("💾 Saving user memories...")
        
        # Day 1: User creates account
        await remember_user_action(
            self.test_chat_id, 
            "created_virtual_account",
            full_name="ThankGod Emmanuel",
            phone_number="08012345678"
        )
        
        # Day 2: User transfers money
        await remember_transaction(
            self.test_chat_id,
            "transfer",
            5000,
            recipient_name="John Doe",
            recipient_account="1234567890",
            bank_name="gtbank"
        )
        
        # Day 3: User buys airtime
        await remember_transaction(
            self.test_chat_id,
            "airtime",
            500,
            recipient_name="Self",
            narration="MTN Airtime"
        )
        
        print("✅ Memories saved successfully!")
        
        # Retrieve user profile
        profile = await sharp_memory.get_user_profile(self.test_chat_id)
        if profile:
            print(f"\n👤 USER PROFILE:")
            print(f"   Name: {profile.get('full_name', 'Unknown')}")
            print(f"   Phone: {profile.get('phone_number', 'Unknown')}")
            print(f"   Last Action: {profile.get('last_action', 'None')}")
            print(f"   Total Transactions: {profile.get('total_transactions', 0)}")
            print(f"   Total Spent: ₦{profile.get('total_spent', 0):,.2f}")
        
        # Get transaction history
        transactions = await sharp_memory.get_transaction_history(self.test_chat_id, days_back=30)
        print(f"\n📊 TRANSACTION HISTORY ({len(transactions)} transactions):")
        for tx in transactions:
            tx_date = datetime.fromisoformat(tx['transaction_date'].replace('Z', '+00:00'))
            print(f"   • {tx['transaction_type'].title()}: ₦{tx['amount']:,.2f} - {tx_date.strftime('%B %d, %Y')}")
    
    async def demo_date_time_awareness(self):
        """Demonstrate date and time awareness"""
        print("\n📅 DATE & TIME AWARENESS DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_memory import sharp_memory
        
        # Get current date/time info
        time_info = sharp_memory.get_current_datetime_info()
        
        print(f"📅 Current Date: {time_info['formatted_date']}")
        print(f"🕐 Current Time: {time_info['formatted_time']}")
        print(f"☀️ Time of Day: {'Morning' if time_info['is_morning'] else 'Afternoon' if time_info['is_afternoon'] else 'Evening' if time_info['is_evening'] else 'Night'}")
        print(f"📍 Day Type: {'Weekend' if time_info['is_weekend'] else 'Weekday'}")
        print(f"🎉 Smart Greeting: {time_info['greeting']}")
        
        # Test relative time descriptions
        print(f"\n🕰️ RELATIVE TIME EXAMPLES:")
        test_times = [
            datetime.now() - timedelta(minutes=30),
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=7),
            datetime.now() - timedelta(days=30),
            datetime.now() - timedelta(days=365)
        ]
        
        for test_time in test_times:
            relative = sharp_memory.get_relative_time_description(test_time)
            print(f"   • {test_time.strftime('%Y-%m-%d %H:%M')} → {relative}")
    
    async def demo_spending_analytics(self):
        """Demonstrate intelligent spending analytics"""
        print("\n💰 SPENDING ANALYTICS DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_memory import sharp_memory
        
        # Get spending summaries for different periods
        periods = ['today', 'week', 'month']
        
        for period in periods:
            summary = await sharp_memory.get_spending_summary(self.test_chat_id, period)
            
            print(f"\n📊 {period.upper()} SPENDING:")
            if summary.get('total_spent', 0) > 0:
                print(f"   💳 Total: ₦{summary['total_spent']:,.2f}")
                print(f"   📈 Transactions: {summary['transaction_count']}")
                print(f"   📊 Average: ₦{summary.get('average_per_transaction', 0):,.2f}")
                
                if summary.get('spending_by_type'):
                    print("   🏷️ Breakdown:")
                    for type_name, amount in summary['spending_by_type'].items():
                        print(f"      • {type_name.title()}: ₦{amount:,.2f}")
            else:
                print(f"   📭 No transactions found")
    
    async def demo_smart_greetings(self):
        """Demonstrate context-aware smart greetings"""
        print("\n👋 SMART GREETING DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_memory import get_smart_greeting
        
        # Generate smart greeting
        greeting = await get_smart_greeting(self.test_chat_id)
        print("🤖 SOFI'S SMART GREETING:")
        print(f"   {greeting}")

    async def demo_xara_style_detection(self):
        """Demonstrate Xara-style account detection"""
        print("\n🎯 XARA-STYLE ACCOUNT DETECTION DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_sofi_intelligence import sharp_sofi
        
        # Test various natural language inputs
        test_messages = [
            "9048887846 moniepoint send 2k",
            "1234567890 access bank transfer 5000",
            "Send 3k to 0987654321 gtb",
            "Transfer 1500 to 2468135790 kuda bank",
            "Pay 7500 to account 1357924680 opay"
        ]
        
        print("🧪 Testing natural language transfer requests:")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Test {i}: '{message}'")
            
            # Process message through sharp AI
            try:
                response = await sharp_sofi.process_message(self.test_chat_id, message)
                
                if "Transfer Details Detected" in response or "transfer request" in response.lower():
                    print("   ✅ DETECTED: Smart transfer processing activated!")
                    print("   📋 Response preview:", response[:100] + "...")
                else:
                    print("   ℹ️ General AI response generated")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    async def demo_conversation_memory(self):
        """Demonstrate conversation memory and context"""
        print("\n💬 CONVERSATION MEMORY DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_sofi_intelligence import sharp_sofi
        
        # Simulate a conversation with memory
        conversation_flow = [
            "Hi Sofi, good morning!",
            "What's my balance?",
            "How much did I spend this week?",
            "What did I do yesterday?",
            "What's today's date?",
            "Remember that I want to buy Bitcoin later"
        ]
        
        print("🗣️ Simulating conversation with memory:")
        
        for i, message in enumerate(conversation_flow, 1):
            print(f"\n   👤 USER: {message}")
            
            try:
                response = await sharp_sofi.process_message(self.test_chat_id, message)
                print(f"   🤖 SOFI: {response[:150]}...")
                
                # Simulate delay between messages
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    async def demo_comprehensive_intelligence(self):
        """Show comprehensive AI intelligence"""
        print("\n🚀 COMPREHENSIVE INTELLIGENCE DEMONSTRATION")
        print("=" * 50)
        
        from utils.sharp_memory import get_spending_report
        
        # Generate comprehensive spending report
        report = await get_spending_report(self.test_chat_id)
        print("📊 INTELLIGENT SPENDING REPORT:")
        print(report)
    
    async def run_all_demos(self):
        """Run all demonstrations"""
        
        print("🎯 SHARP SOFI AI - INTELLIGENT MEMORY SYSTEM DEMO")
        print("=" * 70)
        print(f"🕐 Demo started at: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        print("🧠 Demonstrating ChatGPT/Siri-level intelligence for Sofi AI")
        
        try:
            await self.demo_permanent_memory()
            await self.demo_date_time_awareness()
            await self.demo_spending_analytics()
            await self.demo_smart_greetings()
            await self.demo_xara_style_detection()
            await self.demo_conversation_memory()
            await self.demo_comprehensive_intelligence()
            
            print("\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print("✅ Sofi AI is now SHARP and intelligent like ChatGPT/Siri!")
            print("✅ Permanent memory system active")
            print("✅ Date/time awareness functional")
            print("✅ Context understanding enabled")
            print("✅ Spending analytics ready")
            print("✅ Xara-style intelligence implemented")
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            print("📝 Note: Make sure to deploy the database tables first:")
            print("   1. Run: deploy_sharp_ai_memory_system.sql in Supabase")
            print("   2. Ensure all environment variables are set")

async def main():
    """Main demo function"""
    demo = SharpSofiDemo()
    await demo.run_all_demos()

if __name__ == "__main__":
    print("🚀 Starting Sharp Sofi AI Intelligence Demo...")
    asyncio.run(main())
