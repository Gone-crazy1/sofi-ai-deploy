"""
🚀 SOFI AI - MEMORY-OPTIMIZED MAIN APPLICATION
==============================================

Optimized for handling multiple users efficiently on Render Starter Plan.
Implements advanced memory management and connection pooling.

Created for Sofi AI - The Smart Banking Assistant
"""

from flask import Flask, request, jsonify, url_for, render_template
from flask_cors import CORS
import os, requests, hashlib, logging, json, asyncio, tempfile, re
from datetime import datetime
from typing import Dict, Optional, Any
import time
import gc
from io import BytesIO

# Import memory optimization system
from memory_optimizer import (
    memory_optimizer, cache_manager, memory_efficient, 
    singleton_connection, log_memory_stats, emergency_cleanup
)

# Core imports with lazy loading
def get_supabase_client():
    """Lazy-loaded Supabase client with connection pooling"""
    if not hasattr(get_supabase_client, '_client'):
        from supabase import create_client
        get_supabase_client._client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )
    return get_supabase_client._client

def get_openai_client():
    """Lazy-loaded OpenAI client"""
    if not hasattr(get_openai_client, '_client'):
        from openai import OpenAI
        get_openai_client._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return get_openai_client._client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app with memory optimization
app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS configuration
CORS(app)

# Memory-efficient imports (lazy loading)
def get_bank_api():
    if not hasattr(get_bank_api, '_instance'):
        from utils.bank_api import BankAPI
        get_bank_api._instance = BankAPI()
    return get_bank_api._instance

def get_secure_transfer_handler():
    if not hasattr(get_secure_transfer_handler, '_instance'):
        from utils.secure_transfer_handler import SecureTransferHandler
        get_secure_transfer_handler._instance = SecureTransferHandler()
    return get_secure_transfer_handler._instance

def get_paystack_service():
    if not hasattr(get_paystack_service, '_instance'):
        from paystack import get_paystack_service as _get_ps
        get_paystack_service._instance = _get_ps()
    return get_paystack_service._instance

def get_assistant():
    if not hasattr(get_assistant, '_instance'):
        from assistant import get_assistant as _get_assistant
        get_assistant._instance = _get_assistant()
    return get_assistant._instance

# Global variables for efficiency
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("ADMIN_TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@memory_efficient
def send_telegram_message(chat_id, message, parse_mode="HTML", reply_markup=None):
    """Memory-efficient Telegram message sending with HTML parsing for safety"""
    try:
        # Clean up message to prevent HTML parsing errors
        if parse_mode == "HTML":
            # Fix markdown to HTML conversion
            import re
            
            # Convert **bold** to <b>bold</b>
            message = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', message)
            
            # Convert *italic* to <i>italic</i>
            message = re.sub(r'\*(.*?)\*', r'<i>\1</i>', message)
            
            # Escape any remaining problematic characters
            message = message.replace('&', '&amp;')
            message = message.replace('<', '&lt;').replace('>', '&gt;')
            
            # Restore our HTML tags
            message = message.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
            message = message.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        
        url = f"{BASE_URL}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

@memory_efficient
def detect_intent(message):
    """Memory-efficient intent detection with OpenAI fallback and local backup"""
    try:
        # Check cache first
        cache_key = f"intent_{hash(message)}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            logger.info("🚀 Intent served from cache")
            return cached_result
        
        # Enhanced message processing for Nigerian expressions
        from utils.nigerian_expressions import enhance_nigerian_message
        enhanced_analysis = enhance_nigerian_message(message)
        enhanced_message = enhanced_analysis["enhanced_message"]
        
        # Try OpenAI first, with fallback to local detection
        try:
            openai_client = get_openai_client()
            
            # Optimized system prompt
            system_prompt = """You are Sofi AI intent detector. Respond with JSON only:
{
  "intent": "transfer|balance|history|help|greeting|other",
  "confidence": 0.95,
  "amount": 5000,
  "recipient": "John",
  "details": {}
}

Nigerian context:
- "send 5k" = send 5000 naira
- "check balance" = balance inquiry
- "abeg" = please
"""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Switch back to reliable model that works
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Message: {enhanced_message}"}
                ],
                temperature=0.1,
                max_tokens=200  # Limit response size
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Cache the result
            cache_manager.set(cache_key, result)
            return result
            
        except Exception as openai_error:
            logger.warning(f"OpenAI intent detection failed: {openai_error}, using local fallback")
            
            # LOCAL FALLBACK INTENT DETECTION (when OpenAI fails)
            return detect_intent_locally(message, enhanced_message)
        
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        return detect_intent_locally(message, message)

def detect_intent_locally(original_message, enhanced_message):
    """Local intent detection when OpenAI is unavailable"""
    message_lower = enhanced_message.lower()
    
    # Transfer patterns
    transfer_keywords = ['send', 'transfer', 'pay', 'give', 'money', 'naira', '₦']
    amount_patterns = [r'\d+k', r'₦\d+', r'\d+\s*naira', r'\d+,\d+', r'\d{3,}']
    
    # Balance patterns  
    balance_keywords = ['balance', 'account', 'wallet', 'money', 'much', 'check']
    
    # Extract amount if present
    import re
    amount = 0
    for pattern in amount_patterns:
        match = re.search(pattern, message_lower)
        if match:
            amount_str = match.group()
            # Clean and convert
            amount_str = re.sub(r'[₦,naira\s]', '', amount_str)
            if 'k' in amount_str:
                amount = int(float(amount_str.replace('k', '')) * 1000)
            else:
                amount = int(amount_str) if amount_str.isdigit() else 0
            break
    
    # Extract recipient (simple name detection)
    recipient = ""
    words = enhanced_message.split()
    for i, word in enumerate(words):
        if word.lower() in ['to', 'for'] and i + 1 < len(words):
            # Next word might be recipient
            next_word = words[i + 1]
            if next_word.isalpha() and len(next_word) > 2:
                recipient = next_word
                break
    
    # Determine intent
    if any(keyword in message_lower for keyword in transfer_keywords) and (amount > 0 or recipient):
        return {
            "intent": "transfer",
            "confidence": 0.8,
            "amount": amount,
            "recipient": recipient,
            "details": {"method": "local_detection"}
        }
    elif any(keyword in message_lower for keyword in balance_keywords):
        return {
            "intent": "balance", 
            "confidence": 0.9,
            "details": {"method": "local_detection"}
        }
    elif any(word in message_lower for word in ['help', 'what', 'how', 'start']):
        return {
            "intent": "help",
            "confidence": 0.9,
            "details": {"method": "local_detection"}
        }
    elif any(word in message_lower for word in ['hi', 'hello', 'hey', 'good']):
        return {
            "intent": "greeting",
            "confidence": 0.8,
            "details": {"method": "local_detection"}
        }
    else:
        return {
            "intent": "other",
            "confidence": 0.5,
            "details": {"method": "local_detection", "fallback": True}
        }

@memory_efficient
def get_user_balance(chat_id):
    """Memory-efficient balance checking with caching"""
    try:
        # Check cache first (short TTL for balance)
        cache_key = f"balance_{chat_id}"
        cached_balance = cache_manager.get(cache_key)
        if cached_balance and time.time() - cached_balance.get('timestamp', 0) < 30:  # 30 second cache
            return cached_balance['balance']
        
        supabase = get_supabase_client()
        
        # Get user account info
        user_result = supabase.table("users").select("*").eq("telegram_chat_id", chat_id).execute()
        
        if not user_result.data:
            return 0.0
        
        user = user_result.data[0]
        balance = float(user.get("account_balance", 0))
        
        # Cache the balance
        cache_manager.set(cache_key, {
            'balance': balance,
            'timestamp': time.time()
        })
        
        return balance
        
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return 0.0

@app.route('/health')
def health_check():
    """Health check endpoint with memory stats"""
    try:
        memory_stats = memory_optimizer.get_memory_usage()
        
        # Trigger emergency cleanup if memory is high
        if memory_stats.get('percent', 0) > 85:
            emergency_cleanup()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'memory': {
                'usage_mb': round(memory_stats.get('rss_mb', 0), 1),
                'usage_percent': round(memory_stats.get('percent', 0), 1),
                'cache_entries': memory_stats.get('cache_entries', 0),
                'connections': memory_stats.get('connections', 0)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/memory-stats')
def memory_stats():
    """Detailed memory statistics endpoint"""
    try:
        stats = memory_optimizer.get_memory_usage()
        return jsonify({
            'memory_usage': stats,
            'cache_size': len(cache_manager.cache),
            'process_info': {
                'threads': memory_optimizer.process.num_threads(),
                'cpu_percent': memory_optimizer.process.cpu_percent()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup')
def manual_cleanup():
    """Manual memory cleanup endpoint"""
    try:
        memory_optimizer.cleanup_memory()
        return jsonify({
            'status': 'cleanup_completed',
            'memory_after': memory_optimizer.get_memory_usage()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
@memory_efficient
def webhook():
    """Main webhook endpoint with memory optimization"""
    try:
        # Monitor memory at start of request
        if memory_optimizer.monitor_memory(80):  # Cleanup if > 80%
            logger.info("🧹 Memory cleanup triggered by webhook")
        
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({'status': 'error', 'message': 'No JSON data'}), 400
        
        # Process webhook efficiently
        if 'message' in json_data:
            return process_telegram_message(json_data['message'])
        elif 'callback_query' in json_data:
            return process_callback_query(json_data['callback_query'])
        else:
            return jsonify({'status': 'ignored'})
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        # Force garbage collection after each request
        gc.collect()

@memory_efficient
def process_telegram_message(message):
    """Process Telegram message efficiently"""
    try:
        chat_id = str(message['chat']['id'])
        text = message.get('text', '').strip()
        
        if not text:
            return jsonify({'status': 'no_text'})
        
        # Handle common commands efficiently
        if text == '/balance':
            balance = get_user_balance(chat_id)
            send_telegram_message(chat_id, f"💰 Your balance: ₦{balance:,.2f}")
            return jsonify({'status': 'balance_sent'})
        
        elif text == '/start':
            welcome_msg = """🎉 Welcome to Sofi AI!

I'm your smart banking assistant. I can help you:
• 💸 Send money to friends & family
• 💰 Check your account balance
• 📊 View transaction history
• 💱 Buy/sell cryptocurrency

Type your request naturally, like:
"Send ₦5000 to John" or "Check my balance"

Let's get started! 🚀"""
            send_telegram_message(chat_id, welcome_msg)
            return jsonify({'status': 'welcome_sent'})
        
        # For complex messages, use AI assistant with fallback
        intent = detect_intent(text)
        
        if intent['intent'] == 'transfer':
            return handle_transfer_request(chat_id, intent, text)
        elif intent['intent'] == 'balance':
            balance = get_user_balance(chat_id)
            send_telegram_message(chat_id, f"💰 Your current balance: ₦{balance:,.2f}")
            return jsonify({'status': 'balance_sent'})
        else:
            # Fallback system when OpenAI Assistant fails
            try:
                assistant = get_assistant()
                
                # Try to process with assistant
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, assistant.process_message(chat_id, text))
                        response = future.result()
                else:
                    response = asyncio.run(assistant.process_message(chat_id, text))
                
                if isinstance(response, tuple):
                    response_text = response[0]
                else:
                    response_text = response
                    
                send_telegram_message(chat_id, response_text)
                return jsonify({'status': 'ai_response_sent'})
                
            except Exception as assistant_error:
                logger.error(f"Assistant error: {assistant_error}")
                
                # CRITICAL FALLBACK - Basic banking responses when AI fails
                text_lower = text.lower()
                
                if any(word in text_lower for word in ['transfer', 'send', 'money', 'pay']):
                    fallback_msg = """💸 <b>Money Transfer</b>
                    
I can help you transfer money! Please tell me:
1. Amount (e.g., ₦5000)
2. Recipient name or account details

Example: "Send ₦5000 to John" or "Transfer ₦10000 to 1234567890"

<i>Need help? Type 'help' for more options</i> 🚀"""
                    
                elif any(word in text_lower for word in ['balance', 'account', 'wallet']):
                    balance = get_user_balance(chat_id)
                    fallback_msg = f"💰 <b>Account Balance</b>\n\nYour current balance: <b>₦{balance:,.2f}</b>\n\n<i>Type 'transfer' to send money</i> 💸"
                    
                elif any(word in text_lower for word in ['help', 'what', 'how']):
                    fallback_msg = """🤖 <b>Sofi AI Banking Assistant</b>

I can help you with:
• 💸 <b>Send Money</b> - "Send ₦5000 to John"
• 💰 <b>Check Balance</b> - "What's my balance?"
• 📊 <b>Transaction History</b> - "Show transactions"
• 🔄 <b>Account Info</b> - "Account details"

Just type naturally! I understand Nigerian expressions too 🇳🇬"""
                    
                else:
                    fallback_msg = """👋 I'm Sofi AI, your banking assistant!

I can help you:
• Transfer money to friends & family 💸
• Check your account balance 💰
• View transaction history 📊

<b>Try saying:</b> "Send ₦5000 to John" or "Check my balance"

<i>I'm currently experiencing some technical issues but basic functions work!</i> 🔧"""
                
                send_telegram_message(chat_id, fallback_msg)
                return jsonify({'status': 'fallback_response_sent'})
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        send_telegram_message(chat_id, "I'm having a small issue. Please try again! 😅")
        return jsonify({'status': 'error', 'message': str(e)})

@memory_efficient 
def handle_transfer_request(chat_id, intent, original_message):
    """Handle money transfer request efficiently"""
    try:
        amount = intent.get('amount', 0)
        recipient = intent.get('recipient', '')
        
        if not amount or not recipient:
            send_telegram_message(chat_id, 
                "Please specify both amount and recipient. Example: 'Send ₦5000 to John'")
            return jsonify({'status': 'incomplete_transfer'})
        
        # Check balance first
        balance = get_user_balance(chat_id)
        if balance < amount:
            send_telegram_message(chat_id, 
                f"Insufficient balance. You have ₦{balance:,.2f}, but need ₦{amount:,.2f}")
            return jsonify({'status': 'insufficient_balance'})
        
        # Continue with transfer process...
        transfer_handler = get_secure_transfer_handler()
        result = transfer_handler.initiate_transfer(chat_id, amount, recipient)
        
        if result['success']:
            send_telegram_message(chat_id, result['message'])
            return jsonify({'status': 'transfer_initiated'})
        else:
            send_telegram_message(chat_id, f"Transfer failed: {result['message']}")
            return jsonify({'status': 'transfer_failed'})
    
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        send_telegram_message(chat_id, "Transfer failed. Please try again! 😅")
        return jsonify({'status': 'transfer_error'})

@memory_efficient
def process_callback_query(callback_query):
    """Process callback queries efficiently"""
    try:
        chat_id = str(callback_query['message']['chat']['id'])
        data = callback_query.get('data', '')
        
        # Handle callback efficiently
        send_telegram_message(chat_id, f"Processing: {data}")
        return jsonify({'status': 'callback_processed'})
    
    except Exception as e:
        logger.error(f"Callback error: {e}")
        return jsonify({'status': 'callback_error'})

@memory_efficient
def send_reply(chat_id, message, reply_markup=None):
    """Send reply message to user (alias for send_telegram_message)"""
    return send_telegram_message(chat_id, message, reply_markup=reply_markup)

# Security middleware to block attacks
@app.before_request
def security_middleware():
    """Block malicious requests and WordPress vulnerability scans"""
    path = request.path.lower()
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Block WordPress vulnerability scanning attempts
    wordpress_patterns = [
        'wp-includes', 'wp-admin', 'wp-content', 'wp-config',
        'xmlrpc.php', 'wlwmanifest.xml', 'wordpress', 
        '/blog/', '/wp/', '/web/', '/news/', '/shop/',
        '/test/', '/website/', '/wp1/'
    ]
    
    # Block common attack patterns
    attack_patterns = [
        'eval(', 'base64_decode', 'shell_exec', 'system(',
        'phpinfo', 'etc/passwd', '../', '.env', 'config.php',
        'admin/config', 'backup.sql', '.git/', '.htaccess'
    ]
    
    # Check for WordPress attacks
    for pattern in wordpress_patterns:
        if pattern in path:
            logger.warning(f"🚫 Blocked WordPress attack: {request.remote_addr} -> {path}")
            return jsonify({
                'error': 'Not Found',
                'message': 'This is not a WordPress site. This is Sofi AI - Smart Banking Assistant.',
                'status': 404
            }), 404
    
    # Check for other attack patterns
    for pattern in attack_patterns:
        if pattern in path or pattern in request.args.get('q', ''):
            logger.warning(f"🚫 Blocked attack attempt: {request.remote_addr} -> {path}")
            return jsonify({
                'error': 'Forbidden',
                'message': 'Malicious request detected',
                'status': 403
            }), 403
    
    # Block suspicious user agents
    suspicious_agents = [
        'sqlmap', 'nikto', 'nmap', 'masscan', 'zap',
        'burp', 'dirbuster', 'gobuster', 'wpscan'
    ]
    
    for agent in suspicious_agents:
        if agent in user_agent:
            logger.warning(f"🚫 Blocked suspicious user agent: {request.remote_addr}")
            return jsonify({
                'error': 'Forbidden', 
                'status': 403
            }), 403

# Periodic memory monitoring
@app.before_request
def before_request():
    """Monitor memory before each request"""
    if memory_optimizer.monitor_memory(75):  # Warn at 75%
        log_memory_stats()

if __name__ == '__main__':
    # Log initial memory stats
    log_memory_stats()
    logger.info("🚀 Sofi AI Memory-Optimized Version Starting...")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False  # Always False in production
    )
